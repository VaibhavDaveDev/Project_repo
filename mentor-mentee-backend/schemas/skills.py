from pydantic import BaseModel

class SkillBase(BaseModel):
    skill_name: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    skill_id: int

    class Config:
        orm_mode = True