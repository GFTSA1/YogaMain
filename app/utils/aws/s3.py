from loguru import logger
from typing import BinaryIO
from botocore.exceptions import ClientError

from app.settings import settings


class S3Service:
    def __init__(self, client):

        self.client = client
        self.bucket_name = settings.aws_bucket_name

    def upload_file(self, file_object: BinaryIO, content_type: str, object_name: str):
        if not object_name:
            raise ValueError("object_name is required")

        if content_type not in {"video/mp4", "video/webm"}:
            raise ValueError("Invalid content type")

        try:
            self.client.upload_fileobj(
                file_object,
                self.bucket_name,
                object_name,
                ExtraArgs={"ContentType": content_type},
            )
            return True
        except ClientError as e:
            logger.error("S3 upload error {}", e)
            return False

    def delete_file(self, object_name: str):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            logger.error("S3 delete error {}", e)
            return False
