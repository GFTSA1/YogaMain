from sqlmodel import SQLModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    first_name: str
    last_name: str
    mobile_number: str
    role: str


class Studio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    city: str = Field(index=True)
    capacity: int
    address: str


class GroupTrainingInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    level: str
    name: str
    description: str
    duration: int
    price: float


class GroupTrainingStudioUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    group_training_studio_id: int = Field(default=None)
    user_id: int = Field(foreign_key="user.id")


class GroupTrainingStudio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now(ZoneInfo("Europe/Kyiv")))
    studio_id: int = Field(foreign_key="studio.id")


class YogaCourse(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    level: str


class UserYogaCourse(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_paid: bool

    course_id: int = Field(foreign_key="yogacourse.id")
    user_id: int = Field(foreign_key="user.id")


class Trip(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    location: str
    start_date: datetime
    end_date: datetime


class Video(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    link: str

    yoga_course_id: int = Field(foreign_key="yogacourse.id")
