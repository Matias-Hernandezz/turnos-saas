from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.database import get_session
from core.exceptions import AppError
from features.auth.schemas import TokenResponse
from features.auth.dependencies import CurrentUser, get_current_user
from features.tenants.schemas import RegisterBusinessRequest, TenantRead
from features.tenants.service import TenantOnboardingService
from models.tenant import Tenant
from tenancy.dependencies import get_current_tenant
from tenancy.context import TenantContext

router = APIRouter(tags=["tenants"])


@router.post("/onboarding/register", response_model=TokenResponse)
def register_business(
    body: RegisterBusinessRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    try:
        return TenantOnboardingService(session).register_business(body)
    except AppError as exc:
        if exc.code == "slug_taken":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
        if exc.code == "email_taken":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get("/admin/tenants/me", response_model=TenantRead)
def get_my_tenant(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    tenant: Annotated[TenantContext, Depends(get_current_tenant)],
    session: Annotated[Session, Depends(get_session)],
) -> TenantRead:
    row = session.get(Tenant, tenant.tenant_id)
    if row is None or row.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return TenantRead(
        id=str(row.id),
        slug=row.slug,
        name=row.name,
        plan_code=row.plan_code,
        feature_flags=list(row.feature_flags or []),
    )
