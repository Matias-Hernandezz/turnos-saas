from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, select

from core.database import get_session
from core.security import decode_access_token
from core.http_auth import get_bearer_token
from models.tenant import Tenant
from models.user import TenantMembership, User
from tenancy.context import TenantContext
from tenancy.middleware import get_request_tenant_context


def require_public_tenant(request: Request) -> TenantContext:
    ctx = get_request_tenant_context(request)
    if ctx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return ctx


def _tenant_context_from_db(tenant_id: UUID, session: Session) -> TenantContext:
    tenant = session.get(Tenant, tenant_id)
    if tenant is None or tenant.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return TenantContext(
        tenant_id=tenant.id,
        slug=tenant.slug,
        plan_code=tenant.plan_code,
        features=frozenset(tenant.feature_flags or []),
    )


def get_current_tenant(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str | None, Depends(get_bearer_token)],
) -> TenantContext:
    """
    Admin API: tenant desde JWT + membership verificada (A2).
    No aceptar tenant_id del body.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    tenant_id_raw = payload.get("tenant_id")
    if not tenant_id_raw:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant in token")

    tenant_id = UUID(tenant_id_raw)
    user_sub = payload.get("sub")
    if not user_sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.exec(select(User).where(User.email == user_sub)).first()
    if user is None or user.id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    membership = session.exec(
        select(TenantMembership).where(
            TenantMembership.user_id == user.id,
            TenantMembership.tenant_id == tenant_id,
        )
    ).first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of tenant")

    return _tenant_context_from_db(tenant_id, session)


def require_feature(feature_code: str):
    def _dep(ctx: Annotated[TenantContext, Depends(get_current_tenant)]) -> TenantContext:
        if not ctx.has_feature(feature_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_code}' not enabled",
            )
        return ctx

    return _dep
