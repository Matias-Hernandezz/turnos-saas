from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from core.database import get_session
from core.exceptions import AppError, NotFoundError
from features.auth.dependencies import CurrentUser, get_current_user
from features.payments.schemas import (
    CheckoutResponse,
    MpAuthorizeResponse,
    MpConnectionStatus,
    MpOAuthCallbackResponse,
)
from features.payments.service import PaymentService
from tenancy.context import TenantContext
from tenancy.dependencies import get_current_tenant, require_feature

router = APIRouter(prefix="/admin/payments", tags=["payments"])


def _payments(
    session: Annotated[Session, Depends(get_session)],
    tenant: Annotated[TenantContext, Depends(get_current_tenant)],
) -> PaymentService:
    return PaymentService(session, tenant)


@router.get("/status", response_model=MpConnectionStatus)
def payments_status(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[PaymentService, Depends(_payments)],
    tenant: Annotated[TenantContext, Depends(require_feature("online_payments"))],
) -> MpConnectionStatus:
    data = svc.connection_status()
    return MpConnectionStatus(**data)


@router.get("/mp/authorize", response_model=MpAuthorizeResponse)
def mp_authorize(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[PaymentService, Depends(_payments)],
    tenant: Annotated[TenantContext, Depends(require_feature("online_payments"))],
) -> MpAuthorizeResponse:
    try:
        data = svc.oauth_authorize_url()
        return MpAuthorizeResponse(url=data["url"])
    except AppError as exc:
        if exc.code == "feature":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get("/mp/callback", response_model=MpOAuthCallbackResponse)
def mp_oauth_callback(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[PaymentService, Depends(_payments)],
    tenant: Annotated[TenantContext, Depends(require_feature("online_payments"))],
    code: str = Query(...),
    state: str = Query(...),
) -> MpOAuthCallbackResponse:
    try:
        data = svc.oauth_complete(code, state)
        return MpOAuthCallbackResponse(connected=data["connected"], mp_user_id=data.get("mp_user_id"))
    except AppError as exc:
        if exc.code == "oauth_state":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.post("/mp/disconnect", status_code=status.HTTP_204_NO_CONTENT)
def mp_disconnect(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[PaymentService, Depends(_payments)],
    tenant: Annotated[TenantContext, Depends(require_feature("online_payments"))],
) -> None:
    conn = svc.connections.get_active()
    if conn:
        conn.is_active = False
        svc.session.add(conn)
        svc.session.commit()
