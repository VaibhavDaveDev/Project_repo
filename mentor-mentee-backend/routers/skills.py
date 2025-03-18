from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import database, models, schemas, oauth2

router = APIRouter(
    prefix="/skills",
    tags=["skills"],
)

@router.get("/", response_model=List[schemas.Skill])
def read_skills(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieve all skills.
    """
    skills = db.query(models.Skill).offset(skip).limit(limit).all()
    return skills

@router.post("/", response_model=schemas.Skill)
def create_skill(skill: schemas.SkillCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_active_user)):
    """
    Create a new skill (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")

    db_skill = models.Skill(**skill.dict())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill
