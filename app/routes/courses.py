from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..models import YogaCourse
from ..schemas import YogaCourseModel, YogaCoursePatchModel
from ..dependencies import SessionDep, RedisDep
from ..dependencies import (
    get_all_courses_from_cache,
    set_all_courses_to_cache,
    get_course_from_cache,
    set_course_to_cache,
    invalidate_course_cache,
    invalidate_courses_list_cache,
)

courses_router = APIRouter(prefix="/courses", tags=["Courses"])


@courses_router.post("", response_model=YogaCourse, status_code=status.HTTP_201_CREATED)
async def create_courses(
    data: YogaCourseModel, session: SessionDep, redis: RedisDep
) -> YogaCourse:
    course = YogaCourse.model_validate(data)

    session.add(course)
    await session.commit()
    await session.refresh(course)
    await invalidate_courses_list_cache(redis)
    return course


@courses_router.get("", response_model=list[YogaCourse], status_code=status.HTTP_200_OK)
async def get_all_courses(session: SessionDep, redis: RedisDep) -> list[YogaCourse]:
    cached = await get_all_courses_from_cache(redis)
    if cached is not None:
        return cached

    courses = (await session.exec(select(YogaCourse))).all()
    await set_all_courses_to_cache(redis, courses)
    return courses


@courses_router.get(
    "/{course_id}", response_model=YogaCourse, status_code=status.HTTP_200_OK
)
async def get_course(
    course_id: int, session: SessionDep, redis: RedisDep
) -> YogaCourse:
    cached = await get_course_from_cache(redis, course_id)
    if cached is not None:
        return cached

    course = await session.get(YogaCourse, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    await set_course_to_cache(redis, course)
    return course


@courses_router.patch(
    "/{course_id}", response_model=YogaCourse, status_code=status.HTTP_200_OK
)
async def update_course(
    course_id: int, data: YogaCoursePatchModel, session: SessionDep, redis: RedisDep
) -> YogaCourse:
    course = await session.get(YogaCourse, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    course_update = data.model_dump(exclude_unset=True)
    course.sqlmodel_update(course_update)
    session.add(course)
    await session.commit()
    await session.refresh(course)

    await invalidate_course_cache(redis, course_id)
    return course


@courses_router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, session: SessionDep, redis: RedisDep) -> None:
    course = await session.get(YogaCourse, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    await session.delete(course)
    await session.commit()

    await invalidate_course_cache(redis, course_id)
    return None
