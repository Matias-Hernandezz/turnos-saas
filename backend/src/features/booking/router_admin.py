from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from core.database import get_session
from core.exceptions import AppError, NotFoundError
from features.auth.dependencies import CurrentUser, get_current_user
from features.booking.admin_service import BookingAdminService
from features.booking.schemas_admin import (
    BookingAdminListResponse,
    BookingAdminRead,
    BookingAdminUpdate,
)
from tenancy.context import TenantContext
from tenancy.dependencies import get_current_tenant

router = APIRouter(prefix="/admin/bookings", tags=["booking-admin"])


def _admin_bookings(
    session: Annotated[Session, Depends(get_session)],
    tenant: Annotated[TenantContext, Depends(get_current_tenant)],
) -> BookingAdminService:
    return BookingAdminService(session, tenant)


@router.get("", response_model=BookingAdminListResponse)
def list_bookings(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[BookingAdminService, Depends(_admin_bookings)],
    from_date: str = Query(..., description="YYYY-MM-DD"),
    to_date: str = Query(..., description="YYYY-MM-DD"),
    professional_id: UUID | None = Query(None),
) -> BookingAdminListResponse:
    try:
        start = date.fromisoformat(from_date)
        end = date.fromisoformat(to_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date")
    try:
        bookings = svc.list_in_range(start, end, professional_id)
    except AppError as exc:
        if exc.code == "validation":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    return BookingAdminListResponse(
        from_date=from_date,
        to_date=to_date,
        bookings=bookings,
    )


@router.get("/{appointment_id}", response_model=BookingAdminRead)
def get_booking(
    appointment_id: UUID,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[BookingAdminService, Depends(_admin_bookings)],
) -> BookingAdminRead:
    try:
        return svc.get_by_id(appointment_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.patch("/{appointment_id}", response_model=BookingAdminRead)
def update_booking(
    appointment_id: UUID,
    body: BookingAdminUpdate,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[BookingAdminService, Depends(_admin_bookings)],
) -> BookingAdminRead:
    try:
        return svc.update_status(appointment_id, body)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except AppError as exc:
        if exc.code == "invalid_status":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
        if exc.code == "validation":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
