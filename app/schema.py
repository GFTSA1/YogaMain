from enum import Enum

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


class TrainingLevel(str, Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advance = "Advance"


class GroupTrainingModel(SQLModel):
    name: str = Field(min_length=3)
    price: float = Field(ge=1)
    description: Optional[str] = None
    level: TrainingLevel
    duration: int = Field(gt=1)


class GroupTrainingPatchModel(SQLModel):
    name: Optional[str] = Field(default=None, min_length=3)
    price: Optional[float] = Field(default=1, ge=1)
    description: Optional[str] = None
    level: Optional[TrainingLevel] = None
    duration: Optional[int] = Field(default=1, ge=1)
