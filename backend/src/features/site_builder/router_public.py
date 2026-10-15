from typing import Annotated

from fastapi import APIRouter, Depends

from tenancy.context import TenantContext
from tenancy.dependencies import require_public_tenant

router = APIRouter(prefix="/public", tags=["site-public"])


@router.get("/{slug}/site")
def get_published_site(
    slug: str,
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
) -> dict:
    return {"slug": slug, "tenant_id": str(tenant.tenant_id), "published_config": {}}
