from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from core.database import get_session
from core.rate_limit import enforce_public_rate_limit
from core.exceptions import AppError, NotFoundError
from features.booking.schemas import BookingCreatePublic, BookingPublicRead
from features.booking.service import BookingService
from models.appointment import Appointment
from tenancy.context import TenantContext
from tenancy.dependencies import require_public_tenant

router = APIRouter(prefix="/public", tags=["booking-public"])


@router.post("/{slug}/bookings", response_model=BookingPublicRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    slug: str,
    body: BookingCreatePublic,
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
    session: Annotated[Session, Depends(get_session)],
) -> BookingPublicRead:
    enforce_public_rate_limit(request)
    try:
        return BookingService(session, tenant).create_public_hold(body)
    except AppError as exc:
        if exc.code == "slot_unavailable":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
        if exc.code == "validation":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get("/{slug}/bookings/{public_code}")
def get_booking_by_code(
    slug: str,
    public_code: str,
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    if not public_code or len(public_code) < 16:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    row = session.exec(
        select(Appointment).where(
            Appointment.tenant_id == tenant.tenant_id,
            Appointment.public_code == public_code,
        )
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {
        "slug": slug,
        "status": row.status,
        "starts_at": row.starts_at.isoformat(),
        "ends_at": row.ends_at.isoformat(),
        "public_code": row.public_code,
    }


@router.post(
    "/{slug}/bookings/{public_code}/cancel",
    response_model=BookingPublicRead,
)
def cancel_booking(
    slug: str,
    public_code: str,
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
    session: Annotated[Session, Depends(get_session)],
) -> BookingPublicRead:
    if not public_code or len(public_code) < 16:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    try:
        return BookingService(session, tenant).cancel_by_public_code(public_code)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except AppError as exc:
        if exc.code == "invalid_status":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
