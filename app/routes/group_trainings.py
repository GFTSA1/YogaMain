from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import GroupTrainingInfo
from ..schema import GroupTrainingModel, GroupTrainingPatchModel

group_training_router = APIRouter(prefix="/group-trainings", tags=["group-trainings"])

@group_training_router.get("", response_model=list[GroupTrainingModel], status_code=status.HTTP_200_OK)
async def get_group_trainings(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    trainings_info = (await session.exec(select(GroupTrainingInfo))).all()
    return trainings_info

@group_training_router.post("", response_model=GroupTrainingInfo, status_code=status.HTTP_201_CREATED)
async def create_group_training(body: GroupTrainingModel, session: Annotated[AsyncSession, Depends(get_session)]):
    training_info = GroupTrainingInfo.model_validate(body)
    session.add(training_info)
    await session.commit()
    await session.refresh(training_info)

    return training_info

@group_training_router.get("/{training_id}", response_model=GroupTrainingModel, status_code=status.HTTP_200_OK)
async def get_group_training(training_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    training_info = await session.get(GroupTrainingInfo, training_id)

    if training_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training Info not found")

    return training_info

@group_training_router.patch("/{training_id}", response_model=GroupTrainingModel, status_code=status.HTTP_200_OK)
async def update_group_training(data: GroupTrainingPatchModel, training_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    training_info = await session.get(GroupTrainingInfo, training_id)

    if training_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training Info not found")

    training_info_changes = data.model_dump(exclude_unset=True)
    if training_info_changes is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Training update is not provided")

    training_info.sqlmodel_update(training_info_changes)
    await session.commit()
    await session.refresh(training_info)

    return training_info

@group_training_router.delete("/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_training(
    training_id: int, session: Annotated[AsyncSession, Depends(get_session)]
):
    training_info = await session.get(GroupTrainingInfo, training_id)
    if training_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training Info not found")

    await session.delete(training_info)
    await session.commit()
    return None
