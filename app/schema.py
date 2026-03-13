from sqlmodel import SQLModel, Field
from typing import Optional


class YogaCourseModel(SQLModel):
    name: str = Field(min_length=3)
    description: str
    price: float = Field(default=0.0, ge=0)
    level: str


class StudioModel(SQLModel):
    city: str = Field(min_length=3, max_length=168)
    address: str
    capacity: int = Field(gt=1)


class StudioPatchModel(SQLModel):
    city: Optional[str] = Field(default=None, min_length=3, max_length=168)
    address: Optional[str] = None
    capacity: Optional[int] = Field(gt=1, default=None)
