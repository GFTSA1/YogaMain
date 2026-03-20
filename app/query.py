import strawberry
from typing import List
from fastapi import Depends, FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from .schema_graphql import GroupInfoModel, GroupTrainingModel, StudioModel
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
        result = (await db.exec(select(GroupTrainingStudio).join(GroupTrainingInfo, GroupTrainingInfo.id == GroupTrainingStudio.training_info_id).join(Studio, Studio.id == GroupTrainingStudio.studio_id)))
        return result.scalars().all()

schema = strawberry.Schema(query=Query)

app = FastAPI()
graphql_app = GraphQLRouter(schema, context_getter=Context)

app.include_router(graphql_app, prefix="/graphql")