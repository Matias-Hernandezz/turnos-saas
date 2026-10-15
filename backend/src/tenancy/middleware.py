from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlmodel import Session, select

from core.config import get_settings
from core.database import engine
from models.tenant import Tenant
from tenancy.context import TenantContext

TENANT_STATE_KEY = "tenant_context"


def _public_slug_prefix() -> str:
    prefix = get_settings().api_prefix.rstrip("/")
    return f"{prefix}/public/"


class TenantResolutionMiddleware(BaseHTTPMiddleware):
    """
    Resuelve tenant para rutas públicas por path: /api/public/{slug}/...
    Host/subdominio/custom domain: extender aquí con TRUST_PROXY_HEADERS.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.tenant_context = None
        path = request.url.path
        settings = get_settings()

        slug: str | None = None
        public_prefix = _public_slug_prefix()
        if path.startswith(public_prefix):
            rest = path[len(public_prefix) :]
            slug = rest.split("/", 1)[0] if rest else None

        if slug:
            ctx = _load_tenant_by_slug(slug)
            if ctx:
                request.state.tenant_context = ctx

        if settings.trust_proxy_headers:
            # TODO: resolver subdominio / custom domain desde Host validado por proxy
            pass

        return await call_next(request)


def _load_tenant_by_slug(slug: str) -> TenantContext | None:
    with Session(engine) as session:
        tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
        if tenant is None or tenant.id is None:
            return None
        return TenantContext(
            tenant_id=tenant.id,
            slug=tenant.slug,
            plan_code=tenant.plan_code,
            features=frozenset(tenant.feature_flags or []),
        )


def get_request_tenant_context(request: Request) -> TenantContext | None:
    return getattr(request.state, TENANT_STATE_KEY, None)
