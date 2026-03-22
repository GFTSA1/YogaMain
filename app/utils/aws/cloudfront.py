from loguru import logger
from botocore.signers import CloudFrontSigner
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from app.settings import settings


class CloudFrontService:
    def __init__(self, domain: str, key_id: str, private_key: str):
        self.domain = domain
        self.key_id = key_id

        self.private_key = serialization.load_pem_private_key(
            private_key.encode("utf-8"), password=None
        )
        self.signer = CloudFrontSigner(self.key_id, self._rsa_signer)

    def _rsa_signer(self, message):
        return self.private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

    def generate_signed_url(self, object_name: str, expires_in: int) -> str:
        if not object_name or object_name.strip() == "":
            logger.warning("Attempted to generate signed URL without object_name")
            raise ValueError("object_name is required")

        url = f"https://{self.domain}/{object_name}"
        expire_date = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        signed_url = self.signer.generate_presigned_url(url, date_less_than=expire_date)

        return signed_url
