from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MeetingBase(BaseModel):
    mentorship_id: int
    agenda: str
    meeting_date: datetime
    teams_link: Optional[str] = None
    summary: Optional[str] = None

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    agenda: Optional[str] = None
    meeting_date: Optional[datetime] = None
    teams_link: Optional[str] = None
    summary: Optional[str] = None

class Meeting(MeetingBase):
    meeting_id: int

    class Config:
        orm_mode = True

class MeetingAgendaTemplateBase(BaseModel):
    mentor_id: int
    template_name: str
    template_content: str

class MeetingAgendaTemplateCreate(MeetingAgendaTemplateBase):
    pass

class MeetingAgendaTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    template_content: Optional[str] = None

class MeetingAgendaTemplate(MeetingAgendaTemplateBase):
    template_id: int

    class Config:
        orm_mode = True