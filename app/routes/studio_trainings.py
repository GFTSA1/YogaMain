from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import GroupTrainingStudio, GroupTrainingInfo, Studio
from ..schema import GroupTrainingStudioInputModel, GroupTrainingStudioModelPatch, GroupTrainingStudioResponseModel, StudioModel, GroupTrainingModel

group_training_router = APIRouter(
    prefix="/group-training",
    tags=["Group-training"],
)


@group_training_router.get("", response_model=list[GroupTrainingStudioResponseModel])
async def get_group_training_studio(session: AsyncSession = Depends(get_session)):
    statement = (
        select(GroupTrainingInfo, Studio, GroupTrainingStudio)
        .join(
            GroupTrainingStudio,
            GroupTrainingStudio.training_info_id == GroupTrainingInfo.id,
        )
        .join(Studio, Studio.id == GroupTrainingStudio.studio_id)
    )
    trainings = (await session.exec(statement)).all()
    return [GroupTrainingStudioResponseModel(

        studio=StudioModel(
        city=studio.city,
        address=studio.address,
        capacity=studio.capacity,
        ),
        training_info=GroupTrainingModel(
        name=info.name,
        price=info.price,
        description=info.description,
        level=info.level,
        duration=info.duration,
        ),
        id=training.id,
        training_date=training.training_date,
    ) for info, studio, training in trainings]


@group_training_router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupTrainingStudio)
async def create_group_training_studio(
    data: GroupTrainingStudioInputModel,
    session: AsyncSession = Depends(get_session),
):
    training_info = session.get(GroupTrainingInfo, data.training_info_id)
    if not training_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No training info found")

    studio = session.get(Studio, data.studio_id)
    if not studio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No studio found")

    group_training = GroupTrainingStudio.model_validate(data)
    session.add(group_training)
    await session.commit()
    await session.refresh(group_training)

    return group_training