from pydantic import BaseModel
from typing import Optional

class PeriodName(BaseModel):
    en: str
    zh: str

class PeriodBase(BaseModel):
    period_id: str
    name: PeriodName
    start_year: int
    end_year: int
    color: str

class PeriodCreate(PeriodBase):
    pass

class PeriodUpdate(PeriodBase):
    period_id: str
    name: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    color: Optional[str] = None

class Period(PeriodBase):
    id: int

    class Config:
        orm_mode = True
