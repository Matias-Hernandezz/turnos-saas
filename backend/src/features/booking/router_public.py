from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from tenancy.context import TenantContext
from tenancy.dependencies import require_public_tenant

router = APIRouter(prefix="/public", tags=["booking-public"])


@router.get("/{slug}/bookings/{public_code}")
def get_booking_by_code(
    slug: str,
    public_code: str,
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
) -> dict:
    if not public_code or len(public_code) < 16:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"slug": slug, "tenant_id": str(tenant.tenant_id), "status": "pending_implementation"}
