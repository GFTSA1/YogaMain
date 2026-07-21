from enum import Enum
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import model_validator, field_validator, ConfigDict, EmailStr
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


class VideoBase(SQLModel):
    title: str
    is_active: bool = True


class VideoModel(VideoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    duration_seconds: Optional[int]
    url: str


class VideoPatchModel(SQLModel):
    title: Optional[str] = None
    is_active: Optional[bool] = True


class RegisterModel(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    first_name: str = Field(min_length=1, max_length=128)
    last_name: Optional[str] = Field(default=None, max_length=128)
    mobile_number: Optional[str] = Field(default=None, max_length=32)


class LoginModel(SQLModel):
    email: EmailStr
    password: str


class GoogleLoginModel(SQLModel):
    id_token: str


class RefreshRequestModel(SQLModel):
    refresh_token: str


class TokenPairResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"


class UserResponseModel(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None
    mobile_number: Optional[str] = None
    role: str


class UserPatchModel(SQLModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    last_name: Optional[str] = Field(default=None, max_length=128)
    mobile_number: Optional[str] = Field(default=None, max_length=32)
    email: Optional[EmailStr] = None


class PasswordChangeModel(SQLModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)
