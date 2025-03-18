from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import database, models, schemas, oauth2

router = APIRouter(
    prefix="/mentees",
    tags=["mentees"],
)

@router.get("/", response_model=List[schemas.User])
def read_mentees(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieve all mentees.
    """
    mentees = db.query(models.User).filter(models.User.role == "mentee").offset(skip).limit(limit).all()
    return mentees

@router.get("/{mentee_id}", response_model=schemas.User)
def read_mentee(mentee_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve a mentee by ID.
    """
    mentee = db.query(models.User).filter(models.User.user_id == mentee_id, models.User.role == "mentee").first()
    if mentee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentee not found")
    return mentee
