from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..models import GroupTrainingInfo
from ..schemas import GroupTrainingModel, GroupTrainingPatchModel
from ..dependencies import SessionDep

training_info_router = APIRouter(prefix="/training-info", tags=["Trainings-info"])


@training_info_router.get(
    "", response_model=list[GroupTrainingInfo], status_code=status.HTTP_200_OK
)
async def get_group_trainings(session: SessionDep):
    trainings_info = (await session.exec(select(GroupTrainingInfo))).all()
    return trainings_info


@training_info_router.post(
    "", response_model=GroupTrainingInfo, status_code=status.HTTP_201_CREATED
)
async def create_group_training(body: GroupTrainingModel, session: SessionDep):
    training_info = GroupTrainingInfo.model_validate(body)
    session.add(training_info)
    await session.commit()
    await session.refresh(training_info)

    return training_info


@training_info_router.get(
    "/{training_id}", response_model=GroupTrainingModel, status_code=status.HTTP_200_OK
)
async def get_group_training(training_id: int, session: SessionDep):
    training_info = await session.get(GroupTrainingInfo, training_id)

    if training_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Training Info not found"
        )

    return training_info


@training_info_router.patch(
    "/{training_id}", response_model=GroupTrainingModel, status_code=status.HTTP_200_OK
)
async def update_group_training(
    data: GroupTrainingPatchModel, training_id: int, session: SessionDep
):
    training_info = await session.get(GroupTrainingInfo, training_id)

    if training_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Training Info not found"
        )

    training_info_changes = data.model_dump(exclude_unset=True)
    if not training_info_changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training update is not provided",
        )

    training_info.sqlmodel_update(training_info_changes)
    await session.commit()
    await session.refresh(training_info)

    return training_info


@training_info_router.delete("/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_training(training_id: int, session: SessionDep):
    training_info = await session.get(GroupTrainingInfo, training_id)
    if training_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Training Info not found"
        )

    await session.delete(training_info)
    await session.commit()
    return None
