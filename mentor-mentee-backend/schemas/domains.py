from pydantic import BaseModel

class DomainBase(BaseModel):
    domain_name: str

class DomainCreate(DomainBase):
    pass

class Domain(DomainBase):
    domain_id: int

    class Config:
        orm_mode = True