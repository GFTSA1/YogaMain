from sqlmodel import SQLModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo


class PKMixin(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class User(PKMixin, table=True):
    email: str
    first_name: str
    last_name: str
    mobile_number: str
    role: str


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
    description: str
    price: float = Field(default=5.0, gt=0)
    level: str


class UserYogaCourse(PKMixin, table=True):
    is_paid: bool

    course_id: int = Field(foreign_key="yogacourse.id")
    user_id: int = Field(foreign_key="user.id")


class Trip(PKMixin, table=True):
    name: str
    description: str
    location: str
    start_date: datetime
    end_date: datetime


class Video(PKMixin, table=True):
    title: str
    link: str

    yoga_course_id: int = Field(foreign_key="yogacourse.id")
