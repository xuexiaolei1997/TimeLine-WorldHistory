from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class PeriodName(BaseModel):
    """Localized period name"""
    en: str = Field(..., example="Ancient Rome", min_length=1)
    zh: str = Field(..., example="古罗马", min_length=1)

class PeriodBase(BaseModel):
    """Base period model with common fields"""
    name: PeriodName = Field(..., description="Localized period name")
    description: str = Field(
        "", 
        description="Detailed description of the period",
        example="The Roman Empire was the post-Republican period of ancient Rome..."
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
    id: str = Field(..., alias="_id", description="MongoDB ObjectID")
    periodId: str = Field(..., description="Unique period identifier")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
