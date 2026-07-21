from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..models import Studio
from ..schemas import StudioModel, StudioPatchModel
from ..dependencies import SessionDep

studio_router = APIRouter(prefix="/studios", tags=["Studios"])


@studio_router.get("", response_model=list[Studio], status_code=status.HTTP_200_OK)
async def get_studios(session: SessionDep):
    studios = (await session.exec(select(Studio))).all()
    return studios


@studio_router.post("", response_model=Studio, status_code=status.HTTP_201_CREATED)
async def create_studio(body: StudioModel, session: SessionDep) -> Studio:
    studio = Studio.model_validate(body)
    session.add(studio)
    await session.commit()
    await session.refresh(studio)
    return studio


@studio_router.get(
    "/{studio_id}", response_model=StudioModel, status_code=status.HTTP_200_OK
)
async def get_studio(studio_id: int, session: SessionDep):
    studio = await session.get(Studio, studio_id)
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Studio not found"
        )
    return studio


@studio_router.patch(
    "/{studio_id}", response_model=StudioModel, status_code=status.HTTP_200_OK
)
async def update_studio(body: StudioPatchModel, studio_id: int, session: SessionDep):
    studio = await session.get(Studio, studio_id)
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Studio not found"
        )

    studio_changes = body.model_dump(exclude_unset=True)
    if not studio_changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    studio.sqlmodel_update(studio_changes)

    session.add(studio)
    await session.commit()
    await session.refresh(studio)

    return studio


@studio_router.delete("/{studio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_studio(studio_id: int, session: SessionDep):
    studio = await session.get(Studio, studio_id)

    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Studio not found"
        )

    await session.delete(studio)
    await session.commit()
    return None
