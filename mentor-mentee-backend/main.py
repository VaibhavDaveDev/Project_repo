from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from .routers import auth, users, mentors, mentees, courses, mentorships, reports, meetings, skills, domains, admin
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Add project root to Python path

app = FastAPI()

app.include_router(auth.router)  # Include the auth router
app.include_router(users.router)
app.include_router(mentors.router)
app.include_router(mentees.router)
app.include_router(courses.router)
app.include_router(mentorships.router)
app.include_router(reports.router)
app.include_router(meetings.router)
app.include_router(skills.router)
app.include_router(domains.router)
app.include_router(admin.router)

models.Base.metadata.create_all(bind=engine)