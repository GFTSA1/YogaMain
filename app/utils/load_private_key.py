from app.settings import settings


def load_private_key() -> str:
    if not settings.cloudfront_private_key_path:
        raise ValueError("CLOUDFRONT_PRIVATE_KEY_PATH is not set")

    try:
        with open(settings.cloudfront_private_key_path, "rb") as f:
            return f.read().decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to load private key: {e}")
