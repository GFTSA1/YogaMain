from typing import Annotated
from fastapi import Depends
from functools import lru_cache

from ..utils import CloudFrontService, load_private_key
from ..settings import settings


@lru_cache
def get_cloudfront_service() -> CloudFrontService:
    return CloudFrontService(
        domain=settings.cloudfront_domain,
        key_id=settings.cloudfront_key_id,
        private_key=load_private_key()
    )

CloudfrontDep = Annotated[CloudFrontService, Depends(get_cloudfront_service)]