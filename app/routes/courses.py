from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..models import YogaCourse
from ..schema import YogaCourseModel, YogaCoursePatchModel
from ..dependencies import SessionDep


courses_router = APIRouter(prefix="/courses", tags=["Courses"])


@courses_router.post("", response_model=YogaCourse, status_code=status.HTTP_201_CREATED)
async def create_courses(data: YogaCourseModel, session: SessionDep) -> YogaCourse:
    course = YogaCourse.model_validate(data)

    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


@courses_router.get("", response_model=list[YogaCourse], status_code=status.HTTP_200_OK)
async def get_all_courses(session: SessionDep) -> list[YogaCourse]:
    courses = (await session.exec(select(YogaCourse))).all()
    return courses


@courses_router.get(
    "/{course_id}", response_model=YogaCourse, status_code=status.HTTP_200_OK
)
async def get_course(course_id: int, session: SessionDep) -> YogaCourse:
    course = await session.get(YogaCourse, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course


@courses_router.patch(
    "/{course_id}", response_model=YogaCourse, status_code=status.HTTP_200_OK
)
async def update_course(
    course_id: int, data: YogaCoursePatchModel, session: SessionDep
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
    return course


@courses_router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, session: SessionDep) -> None:
    course = await session.get(YogaCourse, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    await session.delete(course)
    await session.commit()
    return None
