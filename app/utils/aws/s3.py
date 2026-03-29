import asyncio

from loguru import logger
from typing import BinaryIO
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor

from app.settings import settings


class S3Service:
    def __init__(self, client):

        self.client = client
        self.bucket_name = settings.aws_bucket_name
        self.executor = ThreadPoolExecutor(max_workers=5)

    def _upload_sync(self, file_object: BinaryIO, content_type: str, object_name: str):
        self.client.upload_fileobj(
            file_object,
            self.bucket_name,
            object_name,
            ExtraArgs={"ContentType": content_type},
        )

    async def upload_file(
        self, file_object, content_type: str, object_name: str
    ) -> bool:
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self.executor,
                self._upload_sync,
                file_object,
                content_type,
                object_name,
            )
            return True

        except ClientError as e:
            logger.error("S3 upload error: {}", e)
            return False

    def delete_file(self, object_name: str) -> bool:
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
            return True

        except ClientError as e:
            logger.error("S3 delete error: {}", e)
            return False
