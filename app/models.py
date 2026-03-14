from sqlalchemy import Column
from sqlalchemy.types import DateTime
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional


class PKMixin(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class UserTrip(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    trip_id: int = Field(foreign_key="trip.id")


class UserYogaCourse(PKMixin, table=True):
    is_paid: bool

    course_id: int = Field(foreign_key="yogacourse.id")
    user_id: int = Field(foreign_key="user.id")


class User(PKMixin, table=True):
    email: str
    first_name: str
    last_name: str
    mobile_number: str
    role: str

    trips: list["Trip"] = Relationship(back_populates="users", link_model=UserTrip)
    courses: list["YogaCourse"] = Relationship(
        back_populates="users", link_model=UserYogaCourse
    )


class Studio(PKMixin, table=True):
    city: str = Field(index=True)
    capacity: int
    address: str


class GroupTrainingInfo(PKMixin, table=True):
    level: str
    name: str
    description: str
    duration: int
    price: float


class GroupTrainingStudioUser(PKMixin, table=True):
    group_training_studio_id: int = Field(default=None)
    user_id: int = Field(foreign_key="user.id")


class GroupTrainingStudio(PKMixin, table=True):
    date: datetime = Field(default_factory=datetime.now(ZoneInfo("Europe/Kyiv")))
    studio_id: int = Field(foreign_key="studio.id")


class YogaCourse(PKMixin, table=True):
    name: str = Field(min_length=3)
    description: Optional[str]
    price: float = Field(default=5.0, gt=0)
    level: str

    videos: list["Video"] = Relationship(back_populates="course")
    users: list["User"] = Relationship(
        back_populates="courses", link_model=UserYogaCourse
    )


class Trip(PKMixin, table=True):
    name: str = Field(min_length=3, index=True)
    description: Optional[str]
    location: str = Field(nullable=False, index=True)
    start_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    end_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    users: list["User"] = Relationship(back_populates="trips", link_model=UserTrip)


class Video(PKMixin, table=True):
    title: str
    link: str
    yoga_course_id: int = Field(foreign_key="yogacourse.id")

    course: Optional["YogaCourse"] = Relationship(back_populates="videos")
