from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import Video
from ..schema import VideoModel
from ..utils import S3Service, CloudFrontService, load_private_key
from ..dependencies import get_s3_service, get_cloudfront_service, SessionDep

videos_router = APIRouter(prefix="/video", tags=["Video"])


@videos_router.post("", response_model=Video, status_code=status.HTTP_201_CREATED)
async def upload_video(
    session: SessionDep
):

    pass
