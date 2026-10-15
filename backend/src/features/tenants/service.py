from sqlmodel import Session, select

from core.exceptions import AppError, NotFoundError
from core.security import create_access_token, hash_password
from features.auth.schemas import TokenResponse
from features.tenants.presets import RUBRO_PRESETS
from features.tenants.schemas import RegisterBusinessRequest
from models.catalog import Service
from models.page_config import PageConfig
from models.tenant import Tenant
from models.user import TenantMembership, User
from tenancy.plan_seed import feature_flags_for_plan_code


class TenantOnboardingService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register_business(self, body: RegisterBusinessRequest) -> TokenResponse:
        if self.session.exec(select(Tenant).where(Tenant.slug == body.slug)).first():
            raise AppError("Slug already in use", code="slug_taken")
        if self.session.exec(select(User).where(User.email == body.owner_email)).first():
            raise AppError("Email already registered", code="email_taken")

        plan_code = "basic"
        flags = feature_flags_for_plan_code(self.session, plan_code)

        tenant = Tenant(
            slug=body.slug,
            name=body.name,
            plan_code=plan_code,
            feature_flags=flags,
        )
        self.session.add(tenant)
        self.session.flush()

        user = User(
            email=body.owner_email,
            hashed_password=hash_password(body.owner_password),
        )
        self.session.add(user)
        self.session.flush()

        assert tenant.id is not None and user.id is not None

        self.session.add(
            TenantMembership(user_id=user.id, tenant_id=tenant.id, role="owner"),
        )

        preset = RUBRO_PRESETS.get(body.rubro, RUBRO_PRESETS.get("barberia", {}))
        self.session.add(
            PageConfig(
                tenant_id=tenant.id,
                draft_config={
                    "template": "minimal",
                    "sections": preset.get("default_sections", []),
                },
                published_config={},
            )
        )

        for svc in preset.get("sample_services", []):
            self.session.add(
                Service(
                    tenant_id=tenant.id,
                    name=svc["name"],
                    duration_minutes=svc["duration_minutes"],
                    price_cents=svc.get("price_cents", 0),
                )
            )

        self.session.commit()

        token = create_access_token(
            subject=user.email,
            tenant_id=tenant.id,
            roles=["owner"],
        )
        return TokenResponse(access_token=token)
