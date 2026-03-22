from loguru import logger
from botocore.signers import CloudFrontSigner

from app.settings import settings


class CloudFrontService:
    def __init__(self):
        pass

    def generate_signed_url(self, object_name: str, expires_in: int) -> str:
        if not object_name:
            raise ValueError("object_name is required")
