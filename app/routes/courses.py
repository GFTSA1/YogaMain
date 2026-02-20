from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import YogaCourse

# from ..mock import User

courses_router = APIRouter(prefix="/courses", tags=["Courses"])


# @courses_router.post("", response_model=YogaCourse, status_code=status.HTTP_201_CREATED)
# async def create_courses(
#     course: YogaCourse, session: Annotated[AsyncSession, Depends(get_session)]
# ):
#     # course = course.model_validate()

#     # session.add(course)
#     pass


@courses_router.get("", response_model=List[YogaCourse], status_code=status.HTTP_200_OK)
async def get_all_courses(session: Annotated[AsyncSession, Depends(get_session)]):
    courses = (await session.exec(select(YogaCourse))).all()
    return courses
