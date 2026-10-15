import hashlib
import hmac

from core.config import get_settings
from core.exceptions import AppError


def verify_mp_signature(
    *,
    secret: str,
    x_signature: str,
    x_request_id: str,
    data_id: str,
) -> None:
    parts = {}
    for segment in x_signature.split(","):
        segment = segment.strip()
        if "=" in segment:
            key, value = segment.split("=", 1)
            parts[key.strip()] = value.strip()
    ts = parts.get("ts")
    v1 = parts.get("v1")
    if not ts or not v1:
        raise AppError("Invalid signature header", code="webhook_signature")
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    digest = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(digest, v1):
        raise AppError("Invalid webhook signature", code="webhook_signature")
