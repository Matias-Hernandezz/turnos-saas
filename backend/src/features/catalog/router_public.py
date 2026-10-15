from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.database import get_session
from features.catalog.schemas import ProfessionalRead, ServiceRead
from features.catalog.service import CatalogService
from tenancy.context import TenantContext
from tenancy.dependencies import require_public_tenant

router = APIRouter(prefix="/public", tags=["catalog-public"])


def _catalog_public(
    session: Annotated[Session, Depends(get_session)],
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
) -> CatalogService:
    return CatalogService(session, tenant)


@router.get("/{slug}/services", response_model=list[ServiceRead])
def list_public_services(
    slug: str,
    catalog: Annotated[CatalogService, Depends(_catalog_public)],
) -> list[ServiceRead]:
    return catalog.list_active_services()


@router.get("/{slug}/professionals", response_model=list[ProfessionalRead])
def list_public_professionals(
    slug: str,
    catalog: Annotated[CatalogService, Depends(_catalog_public)],
) -> list[ProfessionalRead]:
    return catalog.list_active_professionals()
