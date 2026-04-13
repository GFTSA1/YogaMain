from typing import Optional
from fastapi import APIRouter, status, File, UploadFile, Form, Query

from ..schemas import VideoModel, VideoPatchModel
from ..settings import settings
from ..utils import VideoService, FileValidator, to_video_response
from ..dependencies import SessionDep, S3ServiceDep, CloudfrontDep

videos_router = APIRouter(prefix="/courses/{course_id}/videos", tags=["Video"])


@videos_router.post("", response_model=VideoModel, status_code=status.HTTP_201_CREATED)
async def upload_video(
    course_id: int,
    session: SessionDep,
    s3: S3ServiceDep,
    cloudfront: CloudfrontDep,
    title: str = Form(...),
    file: UploadFile = File(...),
):

    ext = FileValidator.validate_video(file)

    await VideoService.ensure_course_exists(session, course_id)
    await VideoService.ensure_unique_title(session, title, course_id)

    object_name = await VideoService.upload_to_s3(s3, file, ext)

    video = await VideoService.create_video(session, title, course_id, object_name, s3)

    return to_video_response(video, cloudfront)


@videos_router.get(
    "",
    response_model=list[VideoModel],
    status_code=status.HTTP_200_OK,
)
async def get_videos(
    course_id: int,
    session: SessionDep = SessionDep,
    cloudfront: CloudfrontDep = CloudfrontDep,
    is_active: Optional[bool] = Query(default=None),
):
    videos = await VideoService.get_list(
        session,
        course_id=course_id,
        is_active=is_active,
    )

    return [to_video_response(v, cloudfront) for v in videos]


@videos_router.get(
    "/{video_id}",
    response_model=VideoModel,
)
async def get_video(
    course_id: int,
    video_id: int,
    session: SessionDep,
    cloudfront: CloudfrontDep,
):
    video = await VideoService.get_by_id_and_course(session, video_id, course_id)
    return to_video_response(video, cloudfront)


@videos_router.patch(
    "/{video_id}",
    response_model=VideoPatchModel,
    status_code=status.HTTP_200_OK,
)
async def update_video(
    course_id: int,
    video_id: int,
    data: VideoPatchModel,
    session: SessionDep,
    cloudfront: CloudfrontDep,
):
    video = await VideoService.get_by_id_and_course(
        session,
        video_id,
        course_id,
    )

    update_data = data.model_dump(exclude_unset=True)

    video.sqlmodel_update(update_data)

    session.add(video)
    await session.commit()
    await session.refresh(video)

    return to_video_response(video, cloudfront)


@videos_router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    course_id: int, video_id: int, session: SessionDep, s3: S3ServiceDep
):
    video = await VideoService.get_by_id_and_course(session, video_id, course_id)

    await VideoService.delete_video(session, video, s3)
