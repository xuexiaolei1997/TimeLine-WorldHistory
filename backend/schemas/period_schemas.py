from pydantic import BaseModel
from typing import Optional

class PeriodName(BaseModel):
    en: str
    zh: str

class PeriodBase(BaseModel):
    periodId: str
    name: PeriodName
    startYear: int
    endYear: int
    color: str

class PeriodCreate(PeriodBase):
    pass

class PeriodUpdate(PeriodBase):
    periodId: str
    name: PeriodName
    startYear: int
    endYear: int
    color: str

class Period(PeriodBase):
    _id: int

    class Config:
        orm_mode = True
