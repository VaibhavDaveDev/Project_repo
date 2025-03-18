from pydantic import BaseModel
from datetime import date
from typing import Optional

class ProgressReportBase(BaseModel):
    mentorship_id: int
    report_text: str
    report_date: date
    ai_insights: Optional[str] = None

class ProgressReportCreate(ProgressReportBase):
    pass

class ProgressReportUpdate(BaseModel):
    report_text: Optional[str] = None
    report_date: Optional[date] = None
    ai_insights: Optional[str] = None

class ProgressReport(ProgressReportBase):
    report_id: int

    class Config:
        orm_mode = True