from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import database, models, schemas, oauth2
from datetime import datetime

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)

@router.post("/", response_model=schemas.Meeting)
def create_meeting(
    meeting: schemas.MeetingCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Create a meeting for a mentorship.
    """
    # Check if the mentorship exists
    mentorship = db.query(models.Mentorship).filter(models.Mentorship.mentorship_id == meeting.mentorship_id).first()
    if not mentorship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentorship not found")

    # Check if the current user is the mentor for the mentorship
    if current_user.user_id != mentorship.mentor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create meetings for your own mentorships.",
        )

    db_meeting = models.Meeting(**meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@router.get("/mentorship/{mentorship_id}", response_model=List[schemas.Meeting])
def read_meetings_for_mentorship(
    mentorship_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Retrieve all meetings for a specific mentorship.
    """
    # Check if the mentorship exists
    mentorship = db.query(models.Mentorship).filter(models.Mentorship.mentorship_id == mentorship_id).first()
    if not mentorship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentorship not found")

    # Check if the current user is the mentor or mentee for the mentorship, or an admin
    if (
        current_user.user_id != mentorship.mentor_id
        and current_user.user_id != mentorship.mentee_id
        and current_user.role != "admin"
        and current_user.role != "super_admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view meetings for your own mentorships or you are not an admin.",
        )

    meetings = (
        db.query(models.Meeting)
        .filter(models.Meeting.mentorship_id == mentorship_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return meetings

@router.post("/create_template", response_model=schemas.MeetingAgendaTemplate)
def create_meeting_template(
    template: schemas.MeetingAgendaTemplateCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Create a meeting agenda template (Mentor only).
    """
    # Check if the current user is a mentor
    if current_user.role != "mentor" and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can create meeting templates.",
        )

    db_template = models.MeetingAgendaTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/get_templates", response_model=List[schemas.MeetingAgendaTemplate])
def get_meeting_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Get all meeting agenda templates (Mentor only).
    """
    # Check if the current user is a mentor
    if current_user.role != "mentor" and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can get meeting templates.",
        )

    templates = db.query(models.MeetingAgendaTemplate).offset(skip).limit(limit).all()
    return templates