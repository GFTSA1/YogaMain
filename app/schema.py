from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import model_validator
from typing_extensions import Self


class YogaCourseModel(SQLModel):
    name: str = Field(min_length=3)
    description: str
    price: float = Field(default=0.0, ge=0)
    level: str


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
