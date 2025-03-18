from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import database, models, schemas, oauth2

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)

@router.get("/", response_model=List[schemas.Course])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieve all courses.
    """
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=schemas.Course)
def read_course(course_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve a course by ID.
    """
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course

@router.post("/", response_model=schemas.Course)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Create a new course (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.put("/{course_id}", response_model=schemas.Course)
def update_course(
    course_id: int,
    course: schemas.CourseUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Update an existing course (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    db_course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    for key, value in course.dict(exclude_unset=True).items():
        setattr(db_course, key, value)

    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/{course_id}", response_model=schemas.Course)
def delete_course(
    course_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_active_user),
):
    """
    Delete a course (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    db_course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    db.delete(db_course)
    db.commit()
    return db_course