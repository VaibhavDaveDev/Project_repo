from pydantic import BaseModel
from typing import Optional

class CourseBase(BaseModel):
    course_name: str
    description: Optional[str] = None
    lms_link: Optional[str] = None
    domain_id: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    description: Optional[str] = None
    lms_link: Optional[str] = None
    domain_id: Optional[int] = None

class Course(CourseBase):
    course_id: int

    class Config:
        orm_mode = True
