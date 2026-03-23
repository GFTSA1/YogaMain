import uuid

from typing import Annotated
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import Video, YogaCourse

from ..dependencies import SessionDep, S3ServiceDep

videos_router = APIRouter(prefix="/video", tags=["Video"])


@videos_router.post("", response_model=Video, status_code=status.HTTP_201_CREATED)
async def upload_video(
    session: SessionDep,
    s3: S3ServiceDep,
    title: str = Form(...),
    course_id: int = Form(...),
    file: UploadFile = File(...),
):

    allowed_types = {"video/mp4", "video/webm"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type"
        )

    course = await session.get(YogaCourse, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yoga course not found",
        )

    existing_video = (
        await session.exec(
            select(Video).where(Video.title == title, Video.yoga_course_id == course_id)
        )
    ).first()

    if existing_video:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Video already exists in this course",
        )

    file_id = uuid.uuid4()
    extension = file.filename.split(".")[-1] if file.filename else "mp4"
    object_name = f"videos/{file_id}.{extension}"

    upload = s3.upload_file(file.file, file.content_type, object_name)

    if not upload:
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
        s3.delete_file(object_name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Video already exists",
        )

    return video
