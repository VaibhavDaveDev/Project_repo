from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from . import database, models, schemas, oauth2

router = APIRouter(
    prefix="/mentorships",
    tags=["mentorships"],
)

@router.post("/", response_model=schemas.Mentorship)
def apply_for_mentorship(
    mentorship: schemas.MentorshipCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Apply for a mentorship.
    """
    # Ensure the user applying is the mentee
    if current_user.user_id != mentorship.mentee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only apply for mentorships as yourself.",
        )

    # Check if the mentor and mentee exist
    mentor = db.query(models.User).filter(
        models.User.user_id == mentorship.mentor_id, models.User.role == "mentor"
    ).first()
    mentee = db.query(models.User).filter(
        models.User.user_id == mentorship.mentee_id, models.User.role == "mentee"
    ).first()
    course = db.query(models.Course).filter(
        models.Course.course_id == mentorship.course_id
    ).first()

    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mentor ID"
        )
    if not mentee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mentee ID"
        )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid course ID"
        )

    db_mentorship = models.Mentorship(**mentorship.dict())
    db.add(db_mentorship)
    db.commit()
    db.refresh(db_mentorship)
    return db_mentorship


@router.get("/mentor/{mentor_id}", response_model=List[schemas.Mentorship])
def read_mentorships_for_mentor(
    mentor_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Retrieve all mentorships for a specific mentor.
    """
    if (
        current_user.user_id != mentor_id
        and current_user.role != "admin"
        and current_user.role != "super_admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own mentorships or you are not an admin.",
        )
    mentorships = (
        db.query(models.Mentorship)
        .filter(models.Mentorship.mentor_id == mentor_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return mentorships


@router.get("/mentee/{mentee_id}", response_model=List[schemas.Mentorship])
def read_mentorships_for_mentee(
    mentee_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Retrieve all mentorships for a specific mentee.
    """
    if (
        current_user.user_id != mentee_id
        and current_user.role != "admin"
        and current_user.role != "super_admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own mentorships or you are not an admin.",
        )
    mentorships = (
        db.query(models.Mentorship)
        .filter(models.Mentorship.mentee_id == mentee_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return mentorships


@router.put("/{mentorship_id}/accept", response_model=schemas.Mentorship)
def accept_mentorship(
    mentorship_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Accept a mentorship (Mentor only).
    """
    mentorship = (
        db.query(models.Mentorship)
        .filter(models.Mentorship.mentorship_id == mentorship_id)
        .first()
    )
    if not mentorship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mentorship not found"
        )

    if current_user.user_id != mentorship.mentor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only accept mentorships assigned to you.",
        )

    mentorship.status = "accepted"
    db.commit()
    db.refresh(mentorship)
    return mentorship


@router.put("/{mentorship_id}/reject", response_model=schemas.Mentorship)
def reject_mentorship(
    mentorship_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Reject a mentorship (Mentor only).
    """
    mentorship = (
        db.query(models.Mentorship)
        .filter(models.Mentorship.mentorship_id == mentorship_id)
        .first()
    )
    if not mentorship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mentorship not found"
        )

    if current_user.user_id != mentorship.mentor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only reject mentorships assigned to you.",
        )

    mentorship.status = "rejected"
    db.commit()
    db.refresh(mentorship)
    return mentorship


@router.put("/{mentorship_id}/extend_deadline", response_model=schemas.Mentorship)
def extend_deadline(
    mentorship_id: int,
    extend_days: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Extend the deadline for a mentorship (Mentor only).
    """
    mentorship = (
        db.query(models.Mentorship)
        .filter(models.Mentorship.mentorship_id == mentorship_id)
        .first()
    )
    if not mentorship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mentorship not found"
        )

    if current_user.user_id != mentorship.mentor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only extend deadlines for mentorships assigned to you.",
        )

    if mentorship.end_date:
        mentorship.end_date = mentorship.end_date + timedelta(days=extend_days)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mentorship end date not set.",
        )

    db.commit()
    db.refresh(mentorship)
    return mentorship