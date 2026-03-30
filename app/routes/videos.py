from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form, Query
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import Video, YogaCourse
from ..schemas import VideoModel
from ..settings import settings
from ..utils import VideoService, to_video_response
from ..dependencies import SessionDep, S3ServiceDep

videos_router = APIRouter(prefix="/video", tags=["Video"])


@videos_router.post("", response_model=VideoModel, status_code=status.HTTP_201_CREATED)
async def upload_video(
    session: SessionDep,
    s3: S3ServiceDep,
    title: str = Form(...),
    course_id: int = Form(...),
    file: UploadFile = File(...),
):

    ext = VideoService.validate_file(file)

    await VideoService.ensure_course_exists(session, course_id)
    await VideoService.ensure_unique_title(session, title, course_id)

    object_name = await VideoService.upload_to_s3(s3, file, ext)

    video = await VideoService.create_video(session, title, course_id, object_name, s3)

    return VideoModel(
        id=video.id,
        title=video.title,
        course_id=video.yoga_course_id,
        duration_seconds=video.duration_seconds,
        is_active=video.is_active,
        cdn_url=f"{settings.cloudfront_domain}/{video.s3_key}",
    )


@videos_router.get(
    "",
    response_model=list[VideoModel],
)
async def get_videos(
    session: SessionDep,
    course_id: Optional[int] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
):
    videos = await VideoService.get_list(
        session,
        course_id=course_id,
        is_active=is_active,
    )

    return [
        VideoModel(
            id=v.id,
            title=v.title,
            course_id=v.yoga_course_id,
            duration_seconds=v.duration_seconds,
            is_active=v.is_active,
            cdn_url=f"{settings.cloudfront_domain}/{v.s3_key}",
        )
        for v in videos
    ]


@videos_router.get(
    "/courses/{course_id}/videos/{video_id}",
    response_model=VideoModel,
)
async def get_video(
    course_id: int,
    video_id: int,
    session: SessionDep,
):
    video = await VideoService.get_by_id_and_course(session, video_id, course_id)

    return to_video_response(video)
