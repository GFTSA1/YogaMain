from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import YogaCourse

courses_router = APIRouter(prefix="/courses", tags=["Courses"])


@courses_router.post("", status_code=status.HTTP_201_CREATED)
async def create_courses(
    course: YogaCourse, session: Annotated[AsyncSession, Depends(get_session)]
):
    pass
