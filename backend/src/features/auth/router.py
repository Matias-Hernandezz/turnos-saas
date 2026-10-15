from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.database import get_session
from core.exceptions import AppError
from features.auth.schemas import LoginRequest, TokenResponse
from features.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    try:
        return AuthService(session).login(body)
    except AppError as exc:
        if exc.code == "not_found":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
