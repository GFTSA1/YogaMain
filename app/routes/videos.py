import os
import uuid
import asyncio

from typing import Annotated
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import Video, YogaCourse
from ..settings import settings

from ..dependencies import SessionDep, S3ServiceDep

videos_router = APIRouter(prefix="/video", tags=["Video"])

ALLOWED_TYPES = {"video/mp4", "video/webm"}
ALLOWED_EXT = {".mp4", ".webm"}


@videos_router.post("", response_model=Video, status_code=status.HTTP_201_CREATED)
async def upload_video(
    session: SessionDep,
    s3: S3ServiceDep,
    title: str = Form(...),
    course_id: int = Form(...),
    file: UploadFile = File(...),
):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type",
        )

    course = await session.get(YogaCourse, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Yoga course not found"
        )

    existing = (
        await session.exec(
            select(Video).where(Video.title == title, Video.yoga_course_id == course_id)
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Video already exists in this course",
        )

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        ext = ".mp4"

    file_id = uuid.uuid4()
    object_name = f"videos/{file_id}{ext}"

    upload_ok = await s3.upload_file(file.file, file.content_type, object_name)

    if not upload_ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Upload failed"
        )

    video = Video(
        title=title,
        s3_key=object_name,
        yoga_course_id=course_id,
    )

    try:
        session.add(video)
        await session.commit()
        await session.refresh(video)

    except IntegrityError:
        await session.rollback()

        await asyncio.to_thread(s3.delete_file, object_name)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Video already exists (DB constraint)",
        )

    cdn_url = f"{settings.cloudfront_domain}/{object_name}"

    return {
        "id": video.id,
        "title": video.title,
        "course_id": video.yoga_course_id,
        "cdn_url": cdn_url,
    }
