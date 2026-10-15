from typing import Annotated

from fastapi import APIRouter, Depends

from features.auth.dependencies import CurrentUser, get_current_user
from tenancy.context import TenantContext
from tenancy.dependencies import get_current_tenant, require_feature

router = APIRouter(prefix="/admin/payments", tags=["payments"])


@router.get("/status")
def payments_status(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    tenant: Annotated[TenantContext, Depends(require_feature("online_payments"))],
) -> dict:
    return {"tenant_id": str(tenant.tenant_id), "connected": False}
