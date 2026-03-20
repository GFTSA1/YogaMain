import typing
import strawberry
from datetime import datetime

@strawberry.type
class StudioModel:
    id: int
    city: str
    address: str
    capacity: int

@strawberry.type
class GroupInfoModel:
    id: int
    name: str
    price: float
    description: str
    level: str
    duration: int


@strawberry.type
class GroupTrainingModel:
    datetime: datetime
    info: GroupInfoModel
    studio: StudioModel