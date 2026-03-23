import typing
import strawberry
from os import name

import strawberry
from datetime import datetime

@strawberry.type
class StudioModel:
    id: int
    city: str
    address: str
    capacity: int

@strawberry.input
class GroupInfoRequestModel:
    name: str
    price: float
    description: str
    level: str
    duration: int

@strawberry.type
class GroupInfoModel(GroupInfoRequestModel):
    id: int

@strawberry.input
class GroupInfoPatchModel:
    name: typing.Optional[str] = strawberry.UNSET
    price: typing.Optional[float] = strawberry.UNSET
    description: typing.Optional[str] = strawberry.UNSET
    level: typing.Optional[str] = strawberry.UNSET
    duration: typing.Optional[int] = strawberry.UNSET


@strawberry.type
class GroupTrainingModel:
    datetime: datetime
    info: GroupInfoModel
    studio: StudioModel