from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.database import get_session
from core.exceptions import AppError, NotFoundError
from features.payments.schemas import CheckoutResponse
from features.payments.service import PaymentService
from tenancy.context import TenantContext
from tenancy.dependencies import require_public_tenant

router = APIRouter(prefix="/public", tags=["payments-public"])


def _payments_public(
    session: Annotated[Session, Depends(get_session)],
    tenant: Annotated[TenantContext, Depends(require_public_tenant)],
) -> PaymentService:
    return PaymentService(session, tenant)


@router.post("/{slug}/bookings/{public_code}/checkout", response_model=CheckoutResponse)
def create_checkout(
    slug: str,
    public_code: str,
    svc: Annotated[PaymentService, Depends(_payments_public)],
) -> CheckoutResponse:
    if not public_code or len(public_code) < 16:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if not svc.tenant.has_feature("online_payments"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    try:
        data = svc.create_deposit_checkout(public_code)
        return CheckoutResponse(**data)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except AppError as exc:
        if exc.code in ("hold_expired", "invalid_status"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
        if exc.code == "mp_not_connected":
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
