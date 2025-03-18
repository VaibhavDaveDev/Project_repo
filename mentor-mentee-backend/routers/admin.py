from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import database, models, schemas, oauth2

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get("/dashboard")
def get_admin_dashboard_data(db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_active_user)):
    """
    Retrieve data for the admin dashboard (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")

    total_users = db.query(models.User).count()
    total_mentors = db.query(models.User).filter(models.User.role == "mentor").count()
    total_mentees = db.query(models.User).filter(models.User.role == "mentee").count()
    total_courses = db.query(models.Course).count()
    total_mentorships = db.query(models.Mentorship).count()

    return {
        "total_users": total_users,
        "total_mentors": total_mentors,
        "total_mentees": total_mentees,
        "total_courses": total_courses,
        "total_mentorships": total_mentorships,
    }
