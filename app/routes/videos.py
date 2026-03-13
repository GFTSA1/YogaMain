from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import Video
from ..schema import VideoModel
from ..utils import S3Service

videos_router = APIRouter(prefix="/video", tags=["Video"])


@videos_router.post("", response_model=Video, status_code=status.HTTP_201_CREATED)
async def upload_video(
    session: Annotated[AsyncSession, Depends(get_session)],
    # file: UploadFile = File(..., description="Video lesson"),            
):

    pass
