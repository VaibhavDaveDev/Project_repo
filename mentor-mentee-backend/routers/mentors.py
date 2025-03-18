from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import database, models, schemas, oauth2

router = APIRouter(
    prefix="/mentors",
    tags=["mentors"],
)

@router.get("/", response_model=List[schemas.User])
def read_mentors(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieve all mentors.
    """
    mentors = db.query(models.User).filter(models.User.role == "mentor").offset(skip).limit(limit).all()
    return mentors

@router.get("/{mentor_id}", response_model=schemas.User)
def read_mentor(mentor_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve a mentor by ID.
    """
    mentor = db.query(models.User).filter(models.User.user_id == mentor_id, models.User.role == "mentor").first()
    if mentor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    return mentor

@router.post("/approve/{mentor_id}", response_model=schemas.User)
def approve_mentor(mentor_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_active_user)):
    """
    Approve a mentor application (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    mentor = db.query(models.User).filter(models.User.user_id == mentor_id, models.User.role == "mentor").first()
    if mentor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")

    mentor.is_active = True
    db.commit()
    db.refresh(mentor)
    return mentor

@router.post("/reject/{mentor_id}", response_model=schemas.User)
def reject_mentor(mentor_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_active_user)):
    """
    Reject a mentor application (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    mentor = db.query(models.User).filter(models.User.user_id == mentor_id, models.User.role == "mentor").first()
    if mentor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")

    mentor.is_active = False
    db.commit()
    db.refresh(mentor)
    return mentor

@router.post("/create", response_model=schemas.User)
def create_mentor(user: schemas.UserCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_active_user)):
    """
    Create a mentor account (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = oauth2.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role="mentor",
        profile_picture=user.profile_picture,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user