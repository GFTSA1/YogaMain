import boto3

from fastapi import Depends
from functools import lru_cache
from botocore.config import Config

from app.settings import settings
from app.utils import S3Service


@lru_cache
def get_s3_client():
    config = Config(
        retries={"max_attempts": 5, "mode": "standard"},
    )

    return boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        config=config,
    )


def get_s3_service(client=Depends(get_s3_client)):
    return S3Service(client)
