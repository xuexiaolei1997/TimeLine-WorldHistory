from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class PeriodName(BaseModel):
    """Localized period name"""
    en: str = Field(..., example="Ancient Rome", min_length=1)
    zh: str = Field(..., example="古罗马", min_length=1)

class PeriodDescription(BaseModel):
    """Localized period description"""
    en: str = Field("", example="The Roman Empire was the post-Republican period...")
    zh: str = Field("", example="罗马帝国是古罗马共和国时期之后的时期...")

class PeriodBase(BaseModel):
    """Base period model with common fields"""
    name: PeriodName = Field(..., description="Localized period name")
    description: PeriodDescription = Field(
        default_factory=PeriodDescription,
        description="Localized description of the period"
    )
    startYear: int = Field(..., description="Start year of the period")
    endYear: int = Field(..., description="End year of the period")
    color: str = Field(
        "#ffffff", 
        description="Hex color code for visualization",
        pattern=r"^#[0-9a-fA-F]{6}$"
    )

    @validator("endYear")
    def validate_years(cls, v, values):
        if "startYear" in values and v < values["startYear"]:
            raise ValueError("endYear must be >= startYear")
        return v

class PeriodCreate(PeriodBase):
    """Model for creating new periods"""
    pass

class PeriodUpdate(PeriodBase):
    """Model for updating existing periods"""
    pass

class Period(PeriodBase):
    """Complete period model including database ID"""
    id: str = Field(..., description="MongoDB ObjectID")
    periodId: str = Field(..., description="Unique period identifier")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
