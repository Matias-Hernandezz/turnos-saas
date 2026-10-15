from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_session
from core.exceptions import AppError, NotFoundError
from features.auth.dependencies import CurrentUser, get_current_user
from features.catalog.schemas import (
    ProfessionalCreate,
    ProfessionalRead,
    ProfessionalUpdate,
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)
from features.catalog.service import CatalogService
from sqlmodel import Session
from tenancy.context import TenantContext
from tenancy.dependencies import get_current_tenant

router = APIRouter(prefix="/admin/catalog", tags=["catalog"])


def _catalog(
    session: Annotated[Session, Depends(get_session)],
    tenant: Annotated[TenantContext, Depends(get_current_tenant)],
) -> CatalogService:
    return CatalogService(session, tenant)


@router.get("/services", response_model=list[ServiceRead])
def list_services(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> list[ServiceRead]:
    return catalog.list_services()


@router.post("/services", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    body: ServiceCreate,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> ServiceRead:
    return catalog.create_service(body)


@router.patch("/services/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: UUID,
    body: ServiceUpdate,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> ServiceRead:
    try:
        return catalog.update_service(service_id, body)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: UUID,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> None:
    try:
        catalog.delete_service(service_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")


@router.get("/professionals", response_model=list[ProfessionalRead])
def list_professionals(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> list[ProfessionalRead]:
    return catalog.list_professionals()


@router.post("/professionals", response_model=ProfessionalRead, status_code=status.HTTP_201_CREATED)
def create_professional(
    body: ProfessionalCreate,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> ProfessionalRead:
    try:
        return catalog.create_professional(body)
    except AppError as exc:
        if exc.code == "plan_limit":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
        raise


@router.patch("/professionals/{professional_id}", response_model=ProfessionalRead)
def update_professional(
    professional_id: UUID,
    body: ProfessionalUpdate,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> ProfessionalRead:
    try:
        return catalog.update_professional(professional_id, body)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional not found")


@router.delete("/professionals/{professional_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professional(
    professional_id: UUID,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    catalog: Annotated[CatalogService, Depends(_catalog)],
) -> None:
    try:
        catalog.delete_professional(professional_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional not found")
