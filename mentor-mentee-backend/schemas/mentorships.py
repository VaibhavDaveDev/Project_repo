from pydantic import BaseModel
from datetime import date
from typing import Optional

class MentorshipBase(BaseModel):
    mentor_id: int
    mentee_id: int
    course_id: int
    status: str  # Consider using an Enum for status
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class MentorshipCreate(MentorshipBase):
    pass

class MentorshipUpdate(BaseModel):
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class Mentorship(MentorshipBase):
    mentorship_id: int

    class Config:
        orm_mode = True