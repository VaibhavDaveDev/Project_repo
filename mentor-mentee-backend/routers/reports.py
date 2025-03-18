from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import database, models, schemas, oauth2
from datetime import date

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

@router.post("/", response_model=schemas.ProgressReport)
def create_progress_report(
    report: schemas.ProgressReportCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Create a progress report for a mentorship.
    """
    # Check if the mentorship exists
    mentorship = db.query(models.Mentorship).filter(models.Mentorship.mentorship_id == report.mentorship_id).first()
    if not mentorship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentorship not found")

    # Check if the current user is the mentor for the mentorship
    if current_user.user_id != mentorship.mentor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create progress reports for your own mentorships.",
        )

    db_report = models.ProgressReport(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@router.get("/mentorship/{mentorship_id}", response_model=List[schemas.ProgressReport])
def read_reports_for_mentorship(
    mentorship_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Retrieve all progress reports for a specific mentorship.
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
            detail="You can only view progress reports for your own mentorships or you are not an admin.",
        )

    reports = (
        db.query(models.ProgressReport)
        .filter(models.ProgressReport.mentorship_id == mentorship_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reports
