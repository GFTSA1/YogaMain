from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..models import Trip
from ..schemas import TripModel, TripPatchModel
from ..dependencies import SessionDep


trips_router = APIRouter(prefix="/trips", tags=["Trips"])


@trips_router.post("", response_model=Trip, status_code=status.HTTP_201_CREATED)
async def create_trip(data: TripModel, session: SessionDep) -> Trip:
    trip = Trip.model_validate(data)

    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip


@trips_router.get("", response_model=list[Trip], status_code=status.HTTP_200_OK)
async def get_all_trips(
    session: SessionDep,
) -> list[Trip]:
    trips = (await session.exec(select(Trip))).all()
    return trips


@trips_router.get("/{trip_id}", response_model=Trip, status_code=status.HTTP_200_OK)
async def get_trip(trip_id: int, session: SessionDep) -> Trip:
    trip = await session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )
    return trip


@trips_router.patch("/{trip_id}", response_model=Trip, status_code=status.HTTP_200_OK)
async def update_trip(trip_id: int, data: TripPatchModel, session: SessionDep) -> Trip:
    trip = await session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    trip_update = data.model_dump(exclude_unset=True)

    trip.sqlmodel_update(trip_update)
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip


@trips_router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(trip_id: int, session: SessionDep) -> None:
    trip = await session.get(Trip, trip_id)

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    await session.delete(trip)
    await session.commit()
    return None
