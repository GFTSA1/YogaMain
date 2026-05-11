from sqlalchemy import Column
from sqlalchemy.types import DateTime
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional
from sqlalchemy import UniqueConstraint


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
    email: str = Field(index=True, unique=True)
    first_name: str
    last_name: Optional[str] = None
    mobile_number: Optional[str] = None
    role: str = Field(default="user")
    password_hash: Optional[str] = None
    google_sub: Optional[str] = Field(default=None, index=True, unique=True)

    trips: list["Trip"] = Relationship(back_populates="users", link_model=UserTrip)
    courses: list["YogaCourse"] = Relationship(
        back_populates="users", link_model=UserYogaCourse
    )
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")


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


class GroupTrainingStudio(PKMixin, table=True):
    __tablename__ = "grouptrainingstudio"
    __table_args__ = (UniqueConstraint("training_info_id", "studio_id"),)

    training_date: datetime
    studio_id: int | None = Field(
        foreign_key="studio.id", ondelete="SET NULL", default=None
    )
    training_info_id: int = Field(
        foreign_key="grouptraininginfo.id", ondelete="CASCADE"
    )


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
    __table_args__ = (UniqueConstraint("yoga_course_id", "title"),)

    title: str = Field(nullable=False)
    s3_key: str = Field(unique=True, nullable=False)
    duration_seconds: Optional[int] = None
    is_active: bool = Field(default=True)
    yoga_course_id: int = Field(foreign_key="yogacourse.id", nullable=False)

    course: "YogaCourse" = Relationship(back_populates="videos")


class RefreshToken(PKMixin, table=True):
    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)
    token_hash: str = Field(unique=True, nullable=False)
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at: datetime = Field(nullable=False)
    revoked_at: Optional[datetime] = None

    user: "User" = Relationship(back_populates="refresh_tokens")
