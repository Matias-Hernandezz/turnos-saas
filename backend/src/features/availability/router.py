from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlmodel import Session

from core.database import get_session
from core.rate_limit import enforce_public_rate_limit
from core.exceptions import NotFoundError
from features.auth.dependencies import CurrentUser, get_current_user
from features.availability.schemas import (
    SlotRead,
    SlotsResponse,
    WorkingHoursCreate,
    WorkingHoursRead,
    WorkingHoursUpdate,
)
from features.availability.service import AvailabilityAdminService
from features.availability.slots_service import AvailabilitySlotsService
from tenancy.context import TenantContext
from tenancy.dependencies import get_current_tenant, require_public_tenant

router = APIRouter(tags=["availability"])


def _availability_admin(
    session: Annotated[Session, Depends(get_session)],
    tenant: Annotated[TenantContext, Depends(get_current_tenant)],
) -> AvailabilityAdminService:
    return AvailabilityAdminService(session, tenant)


@router.get("/public/{slug}/slots", response_model=SlotsResponse)
def get_slots(
    slug: str,
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
    session: Annotated[Session, Depends(get_session)],
    service_id: str = Query(...),
    day: str = Query(..., description="YYYY-MM-DD"),
    professional_id: str | None = Query(None),
) -> SlotsResponse:
    enforce_public_rate_limit(request)
    try:
        parsed_day = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid day")
    svc = AvailabilitySlotsService(session, tenant.tenant_id)
    try:
        pro_uuid = UUID(professional_id) if professional_id else None
        slots = svc.list_slots(
            service_id=UUID(service_id),
            day=parsed_day,
            professional_id=pro_uuid,
        )
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")
    return SlotsResponse(
        day=day,
        service_id=service_id,
        slots=[SlotRead(**s) for s in slots],
    )


@router.get("/admin/availability/working-hours", response_model=list[WorkingHoursRead])
def list_working_hours(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[AvailabilityAdminService, Depends(_availability_admin)],
    professional_id: UUID | None = Query(None),
) -> list[WorkingHoursRead]:
    return svc.list_working_hours(professional_id)


@router.post(
    "/admin/availability/working-hours",
    response_model=WorkingHoursRead,
    status_code=status.HTTP_201_CREATED,
)
def create_working_hours(
    body: WorkingHoursCreate,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[AvailabilityAdminService, Depends(_availability_admin)],
) -> WorkingHoursRead:
    try:
        return svc.create_working_hours(body)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch("/admin/availability/working-hours/{hours_id}", response_model=WorkingHoursRead)
def update_working_hours(
    hours_id: UUID,
    body: WorkingHoursUpdate,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[AvailabilityAdminService, Depends(_availability_admin)],
) -> WorkingHoursRead:
    try:
        return svc.update_working_hours(hours_id, body)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Working hours not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/admin/availability/working-hours/{hours_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_working_hours(
    hours_id: UUID,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[AvailabilityAdminService, Depends(_availability_admin)],
) -> None:
    try:
        svc.delete_working_hours(hours_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Working hours not found")
