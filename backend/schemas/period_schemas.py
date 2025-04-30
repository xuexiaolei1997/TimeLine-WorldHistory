from pydantic import BaseModel
from typing import Optional

class PeriodBase(BaseModel):
    name: str
    start_year: int
    end_year: int
    color: str

class PeriodCreate(PeriodBase):
    pass

class PeriodUpdate(PeriodBase):
    name: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    color: Optional[str] = None

class Period(PeriodBase):
    id: int

    class Config:
        orm_mode = True
