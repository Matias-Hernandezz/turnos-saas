from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from core.config import get_settings
from core.exceptions import AppError


def create_mp_oauth_state(tenant_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "typ": "mp_oauth",
        "tenant_id": str(tenant_id),
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def parse_mp_oauth_state(state: str) -> UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(
            state,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise AppError("Invalid OAuth state", code="oauth_state") from exc
    if payload.get("typ") != "mp_oauth":
        raise AppError("Invalid OAuth state", code="oauth_state")
    raw = payload.get("tenant_id")
    if not raw:
        raise AppError("Invalid OAuth state", code="oauth_state")
    return UUID(raw)
