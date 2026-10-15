from typing import Annotated

from fastapi import APIRouter, Depends

from features.auth.dependencies import CurrentUser, get_current_user
from tenancy.context import TenantContext
from tenancy.dependencies import get_current_tenant

router = APIRouter(prefix="/admin/site", tags=["site-builder"])


@router.get("/draft")
def get_draft(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    tenant: Annotated[TenantContext, Depends(get_current_tenant)],
) -> dict:
    return {"tenant_id": str(tenant.tenant_id), "draft_config": {}}
