import os
import uuid
import asyncio

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ...models import Video, YogaCourse
from ...schemas import VideoModel
from ...settings import settings


def to_video_response(video: Video) -> VideoModel:
    return VideoModel(
        id=video.id,
        title=video.title,
        course_id=video.yoga_course_id,
        duration_seconds=video.duration_seconds,
        is_active=video.is_active,
        cdn_url=f"{settings.cloudfront_domain}/{video.s3_key}",
    )


ALLOWED_TYPES = {"video/mp4", "video/webm"}
ALLOWED_EXT = {".mp4", ".webm"}


class FileValidator:
    @staticmethod
    def validate_video(file: UploadFile) -> str:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type",
            )

        ext = os.path.splitext(file.filename or "")[1].lower()
        return ext if ext in ALLOWED_EXT else ".mp4"


class VideoService:

    @staticmethod
    async def ensure_course_exists(session, course_id: int):
        course = await session.get(YogaCourse, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yoga course not found",
            )

    @staticmethod
    async def ensure_unique_title(session, title: str, course_id: int):
        existing = (
            await session.exec(
                select(Video).where(
                    Video.title == title,
                    Video.yoga_course_id == course_id,
                )
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Video already exists in this course",
            )

    @staticmethod
    async def upload_to_s3(s3, file, ext: str):
        file_id = uuid.uuid4()
        object_name = f"videos/{file_id}{ext}"

        valid_video = await s3.upload_file(file.file, file.content_type, object_name)

        if not valid_video:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Upload failed",
            )

        return object_name

    @staticmethod
    async def create_video(session, title, course_id, object_name, s3):
        video = Video(
            title=title,
            s3_key=object_name,
            yoga_course_id=course_id,
        )

        try:
            session.add(video)
            await session.commit()
            await session.refresh(video)
            return video

        except IntegrityError:
            await session.rollback()
            await asyncio.to_thread(s3.delete_file, object_name)

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Video already exists (DB constraint)",
            )

    @staticmethod
    async def get_list(
        session,
        course_id: int | None = None,
        is_active: bool | None = None,
    ):
        query = select(Video)

        if course_id is not None:
            query = query.where(Video.yoga_course_id == course_id)

        if is_active is not None:
            query = query.where(Video.is_active == is_active)

        result = await session.exec(query)
        return result.all()

    @staticmethod
    async def get_by_id_and_course(session, video_id: int, course_id: int):
        result = await session.exec(
            select(Video).where(
                Video.id == video_id,
                Video.yoga_course_id == course_id,
            )
        )
        video = result.first()

        if not video:
            raise HTTPException(
                status_code=404,
                detail="Video not found in this course",
            )

        return video
