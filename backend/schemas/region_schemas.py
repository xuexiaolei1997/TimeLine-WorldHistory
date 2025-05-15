from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class RegionName(BaseModel):
    """Localized region name"""
    en: str = Field(..., example="Mediterranean", min_length=1)
    zh: str = Field(..., example="地中海", min_length=1)

class RegionDescription(BaseModel):
    """Localized region description"""
    en: str = Field("", example="The Mediterranean region was central to...")
    zh: str = Field("", example="地中海地区是古代贸易和文化交流的中心")

class RegionCoordinates(BaseModel):
    """Polygon coordinates for region boundary"""
    type: str = Field("Polygon", Literal=True)
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="Array of coordinate arrays representing the polygon boundary",
        example=[[[30, 10], [40, 40], [20, 40], [10, 20], [30, 10]]]
    )

    @validator("coordinates")
    def validate_coordinates(cls, v):
        """Validate polygon coordinates"""
        if len(v) < 1 or len(v[0]) < 4:
            raise ValueError("Polygon must have at least 4 points")
        # Check if first and last points are the same (closed polygon)
        if v[0][0] != v[0][-1]:
            raise ValueError("Polygon must be closed (first and last points must match)")
        return v

class RegionBase(BaseModel):
    """Base region model with common fields"""
    name: RegionName = Field(..., description="Localized region name")
    description: RegionDescription = Field(
        default_factory=RegionDescription,
        description="Localized description of the region"
    )
    boundary: RegionCoordinates = Field(..., description="Polygon boundary coordinates")
    period_id: str = Field(..., description="Associated period ID")
    color: str = Field(
        "#4CAF50",
        description="Hex color code for visualization",
        pattern=r"^#[0-9a-fA-F]{6}$"
    )

class RegionCreate(RegionBase):
    """Model for creating new regions"""
    pass

class RegionUpdate(RegionBase):
    """Model for updating existing regions"""
    pass

class Region(RegionBase):
    """Complete region model including database ID"""
    id: str = Field(..., alias="_id", description="MongoDB ObjectID")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
        validate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
