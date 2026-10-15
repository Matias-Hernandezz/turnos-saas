from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from core.database import get_session
from core.http_auth import get_bearer_token
from core.security import decode_access_token
from models.user import TenantMembership, User


class CurrentUser:
    def __init__(self, user_id: UUID, email: str, tenant_id: UUID | None, roles: list[str]) -> None:
        self.user_id = user_id
        self.email = email
        self.tenant_id = tenant_id
        self.roles = roles

    def has_role(self, role: str) -> bool:
        return role in self.roles


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str | None, Depends(get_bearer_token)],
) -> CurrentUser:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or user.id is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    tenant_id_raw = payload.get("tenant_id")
    tenant_id = UUID(tenant_id_raw) if tenant_id_raw else None
    roles: list[str] = list(payload.get("roles") or [])

    if tenant_id:
        membership = session.exec(
            select(TenantMembership).where(
                TenantMembership.user_id == user.id,
                TenantMembership.tenant_id == tenant_id,
            )
        ).first()
        if membership is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of tenant")
        if membership.role not in roles:
            roles.append(membership.role)

    return CurrentUser(user_id=user.id, email=user.email, tenant_id=tenant_id, roles=roles)
