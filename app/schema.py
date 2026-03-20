from enum import Enum
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import model_validator, field_validator
from typing_extensions import Self


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


class TripModel(SQLModel):
    name: str
    description: str
    location: str
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def check_date(self) -> Self:
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class TripPatchModel(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @model_validator(mode="after")
    def check_dates_patch(self) -> Self:
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError("new end_date must be after start_date")
        return self


class GroupTrainingStudioModel(SQLModel):
    studio_id: int = Field(ge=1)
    training_info_id: int = Field(ge=1)

    training_date: datetime


class GroupTrainingStudioInputModel(GroupTrainingStudioModel):
    @field_validator("training_date")
    @classmethod
    def date_must_be_future(cls, value):
        if value <= datetime.now():
            raise ValueError("Time cannot be in the past")
        return value


class GroupTrainingStudioResponseModel(SQLModel):
    id: int
    studio: StudioModel
    training_info: GroupTrainingModel
    training_date: datetime


class GroupTrainingStudioPatchModel(SQLModel):
    training_date: datetime
    @field_validator("training_date")
    @classmethod
    def date_must_be_future(cls, value):
        if value <= datetime.now():
            raise ValueError("Time cannot be in the past")
        return value
