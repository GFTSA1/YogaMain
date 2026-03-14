from sqlalchemy import Column
from sqlalchemy.types import DateTime
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional


class PKMixin(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class UserTrip(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    trip_id: int = Field(foreign_key="trip.id", primary_key=True)


class UserYogaCourse(SQLModel, table=True):
    course_id: int = Field(foreign_key="yogacourse.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)

    is_paid: bool


class GroupTrainingStudioUser(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    group_training_studio_id: int = Field(
        foreign_key="grouptrainingstudio.id", primary_key=True
    )


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

    trainings: list["GroupTrainingStudio"] = Relationship(back_populates="studio")


class GroupTrainingInfo(PKMixin, table=True):
    level: str
    name: str
    description: str
    duration: int
    price: float

    trainings: list["GroupTrainingStudio"] = Relationship(
        back_populates="training_info"
    )


class GroupTrainingStudio(PKMixin, table=True):
    date: datetime = Field(default_factory=datetime.now(ZoneInfo("Europe/Kyiv")))
    studio_id: int = Field(foreign_key="studio.id")
    training_info_id: int = Field(foreign_key="grouptraininginfo.id")

    studio: "Studio" = Relationship(back_populates="trainings")
    training_info: "GroupTrainingInfo" = Relationship(back_populates="trainings")


class YogaCourse(PKMixin, table=True):
    name: str = Field(min_length=3, nullable=False)
    description: Optional[str] = None
    price: float = Field(default=5.0, gt=0, nullable=False)
    level: str = Field(nullable=False)

    videos: list["Video"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    users: list["User"] = Relationship(
        back_populates="courses",
        link_model=UserYogaCourse,
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
    title: str = Field(nullable=False)
    link: str
    yoga_course_id: int = Field(foreign_key="yogacourse.id", nullable=False)

    course: Optional["YogaCourse"] = Relationship(back_populates="videos")
