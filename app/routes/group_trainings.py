from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import GroupTrainingStudio, GroupTrainingInfo, Studio
from ..schema import (
    GroupTrainingStudioInputModel,
    GroupTrainingStudioPatchModel,
    GroupTrainingStudioResponseModel,
    StudioModel,
    GroupTrainingModel,
)

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
    return [
        GroupTrainingStudioResponseModel(
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
        )
        for info, studio, training in trainings
    ]


@group_training_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=GroupTrainingStudio
)
async def create_group_training_studio(
    data: GroupTrainingStudioInputModel,
    session: AsyncSession = Depends(get_session),
):
    training_info = session.get(GroupTrainingInfo, data.training_info_id)
    if not training_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No training info found"
        )

    studio = session.get(Studio, data.studio_id)
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No studio found"
        )

    group_training = GroupTrainingStudio.model_validate(data)
    session.add(group_training)
    await session.commit()
    await session.refresh(group_training)

    return group_training


@group_training_router.get(
    "/{training_id}",
    response_model=GroupTrainingStudioResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_group_training_studio(
    training_id: int,
    session: AsyncSession = Depends(get_session),
):

    statement = (
        select(GroupTrainingInfo, GroupTrainingStudio, Studio)
        .join(
            GroupTrainingStudio,
            GroupTrainingStudio.training_info_id == GroupTrainingInfo.id,
        )
        .join(
            Studio,
            Studio.id == GroupTrainingStudio.studio_id,
        )
        .where(GroupTrainingStudio.id == training_id)
    )
    training_info, training, studio = (await session.exec(statement)).first()
    if not training_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No training info found"
        )

    return GroupTrainingStudioResponseModel(
        studio=StudioModel(
            city=studio.city,
            address=studio.address,
            capacity=studio.capacity,
        ),
        training_info=GroupTrainingModel(
            name=training_info.name,
            price=training_info.price,
            description=training_info.description,
            level=training_info.level,
            duration=training_info.duration,
        ),
        id=training.id,
        training_date=training.training_date,
    )

@group_training_router.patch(path='/{training_id}', response_model=GroupTrainingStudioResponseModel)
async def patch_group_training(
    training_id: int,
    data: GroupTrainingStudioPatchModel,
    session: AsyncSession = Depends(get_session),
):
    group_training = await session.get(GroupTrainingStudio, training_id)
    if not group_training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No training found")

    group_training_changes = data.model_dump()
    if not group_training_changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )
    group_training.sqlmodel_update(group_training_changes)
    session.add(group_training)

    await session.commit()
    statement = (
        select(GroupTrainingInfo, GroupTrainingStudio, Studio)
        .join(GroupTrainingStudio,
              GroupTrainingStudio.training_info_id == GroupTrainingInfo.id)
        .join(Studio, Studio.id == GroupTrainingStudio.studio_id)
        .where(GroupTrainingStudio.id == training_id)
    )
    group_training, training, studio = (await session.exec(statement)).first()

    return GroupTrainingStudioResponseModel(
        studio=StudioModel(
            city=studio.city,
            address=studio.address,
            capacity=studio.capacity,
        ),
        training_info=GroupTrainingModel(
            name=group_training.name,
            price=group_training.price,
            description=group_training.description,
            level=group_training.level,
            duration=group_training.duration,
        ),
        id=training.id,
        training_date=training.training_date,
    )

@group_training_router.delete(path='/{training_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_training(
        training_id: int,
        session: AsyncSession = Depends(get_session),
):
    group_training = await session.get(GroupTrainingStudio, training_id)
    if not group_training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No training found")

    await session.delete(group_training)
    await session.commit()
    return