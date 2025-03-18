from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import database, models, schemas, oauth2

router = APIRouter(
    prefix="/domains",
    tags=["domains"],
)

@router.get("/", response_model=List[schemas.Domain])
def read_domains(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieve all domains.
    """
    domains = db.query(models.Domain).offset(skip).limit(limit).all()
    return domains

@router.post("/", response_model=schemas.Domain)
def create_domain(domain: schemas.DomainCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_active_user)):
    """
    Create a new domain (Admin only).
    """
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")

    db_domain = models.Domain(**domain.dict())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain
