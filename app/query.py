import strawberry
from typing import List
from fastapi import Depends, FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from .schema_graphql import GroupInfoModel, GroupTrainingModel, StudioModel, GroupInfoRequestModel, GroupInfoPatchModel
from strawberry.fastapi import BaseContext
from .database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from .models import GroupTrainingInfo, Studio, GroupTrainingStudio

class Context(BaseContext):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

@strawberry.type
class Query:
    @strawberry.field
    async def group_trainings_info(self, info: Info) -> List[GroupInfoModel]:
        db = info.context.session
        result = (await db.exec(select(GroupTrainingInfo)))
        return result.scalars().all()

    @strawberry.field
    async def studios(self, info:Info) -> list[StudioModel]:
        db = info.context.session
        result = (await db.exec(select(Studio)))
        return result.scalars().all()

    @strawberry.field
    async def group_trainings(self, info: Info) -> List[GroupTrainingModel]:
        db = info.context.session

        statement = (
        select(GroupTrainingInfo, Studio, GroupTrainingStudio)
        .join(
            GroupTrainingStudio,
            GroupTrainingStudio.training_info_id == GroupTrainingInfo.id,
        )
        .join(Studio, Studio.id == GroupTrainingStudio.studio_id)
    )

        results = (await db.exec(statement)).all()
        print(results)
        return [
            GroupTrainingModel(
                datetime=training.training_date,
                info=GroupInfoModel(
                    id=info.id,
                    name=info.name,
                    price=info.price,
                    description=info.description,
                    level=info.level,
                    duration=info.duration,
                ),
                studio=StudioModel(
                    id=studio.id,
                    city=studio.city,
                    address=studio.address,
                    capacity=studio.capacity,
                )
            )
            for info, studio, training in results
        ]

@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_group_info(self, info: Info, group_info: GroupInfoRequestModel) -> GroupInfoModel:
        session = info.context.session
        training_info = GroupTrainingInfo.model_validate(group_info)
        session.add(training_info)
        await session.commit()
        await session.refresh(training_info)
        return training_info

    @strawberry.mutation
    async def update_group_info(self, training_id:int, info: Info, group_info: GroupInfoPatchModel) -> GroupInfoModel:
        session = info.context.session
        training_info = await session.get(GroupTrainingInfo, training_id)

        if training_info is None:
            raise ValueError(
                "Training Info not found"
            )

        if group_info.name is not strawberry.UNSET:
            training_info.name = group_info.name
        if group_info.price is not strawberry.UNSET:
            training_info.price = group_info.price
        if group_info.description is not strawberry.UNSET:
            training_info.description = group_info.description
        if group_info.level is not strawberry.UNSET:
            training_info.level = group_info.level
        if group_info.duration is not strawberry.UNSET:
            training_info.duration = group_info.duration

        training_info.sqlmodel_update(training_info)
        await session.commit()
        await session.refresh(training_info)

        return training_info

    @strawberry.mutation
    async def delete_group_info(self, training_id:int, info: Info) -> bool:
        session = info.context.session
        training_info = await session.get(GroupTrainingInfo, training_id)

        if training_info is None:
            raise ValueError(
                "Training Info not found"
            )

        await session.delete(training_info)
        await session.commit()
        return True

schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()
graphql_app = GraphQLRouter(schema, context_getter=Context)

app.include_router(graphql_app, prefix="/graphql")