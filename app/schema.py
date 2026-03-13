from typing import Optional
from sqlmodel import SQLModel, Field


class YogaCourseModel(SQLModel):
    name: str = Field(min_length=3)
    description: str
    price: float = Field(default=5.0, gt=0)
    level: str


class YogaCoursePatchModel(SQLModel):
    name: Optional[str] = Field(default=None, min_length=3)
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    level: Optional[str] = None
