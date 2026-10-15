from sqlmodel import Session, select

from core.exceptions import ForbiddenError, NotFoundError
from core.security import create_access_token, verify_password
from features.auth.schemas import LoginRequest, TokenResponse
from models.tenant import Tenant
from models.user import TenantMembership, User


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def login(self, body: LoginRequest) -> TokenResponse:
        user = self.session.exec(select(User).where(User.email == body.email)).first()
        if user is None or not verify_password(body.password, user.hashed_password):
            raise NotFoundError("credentials")

        membership_query = select(TenantMembership).where(TenantMembership.user_id == user.id)
        if body.tenant_slug:
            tenant = self.session.exec(select(Tenant).where(Tenant.slug == body.tenant_slug)).first()
            if tenant is None or tenant.id is None:
                raise NotFoundError("tenant")
            membership_query = membership_query.where(TenantMembership.tenant_id == tenant.id)

        membership = self.session.exec(membership_query).first()
        if membership is None:
            raise ForbiddenError("No tenant membership")

        tenant = self.session.get(Tenant, membership.tenant_id)
        if tenant is None or tenant.id is None:
            raise NotFoundError("tenant")

        token = create_access_token(
            subject=user.email,
            tenant_id=tenant.id,
            roles=[membership.role],
        )
        return TokenResponse(access_token=token)
