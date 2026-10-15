from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.database import engine, init_db
from sqlmodel import Session

from tenancy.plan_seed import ensure_default_plans
from features.analytics.router import router as analytics_router
from features.auth.router import router as auth_router
from features.availability.router import router as availability_router
from features.booking.router_admin import router as booking_admin_router
from features.booking.router_public import router as booking_public_router
from features.catalog.router import router as catalog_router
from features.catalog.router_public import router as catalog_public_router
from features.customers.router import router as customers_router
from features.payments.router import router as payments_router
from features.payments.webhook import router as payments_webhook_router
from features.reviews.router import router as reviews_router
from features.site_builder.router_admin import router as site_builder_admin_router
from features.site_builder.router_public import router as site_builder_public_router
from features.subscriptions.router import router as subscriptions_router
from features.subscriptions.webhook import router as subscriptions_webhook_router
from features.tenants.router import router as tenants_router
from tenancy.middleware import TenantResolutionMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.app_env in ("development", "test"):
        init_db()
        with Session(engine) as session:
            ensure_default_plans(session)
    yield


app = FastAPI(
    title="Turnos SaaS API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantResolutionMiddleware)

prefix = settings.api_prefix.rstrip("/")

app.include_router(auth_router, prefix=prefix)
app.include_router(tenants_router, prefix=prefix)
app.include_router(catalog_router, prefix=prefix)
app.include_router(catalog_public_router, prefix=prefix)
app.include_router(availability_router, prefix=prefix)
app.include_router(booking_admin_router, prefix=prefix)
app.include_router(booking_public_router, prefix=prefix)
app.include_router(customers_router, prefix=prefix)
app.include_router(payments_router, prefix=prefix)
app.include_router(payments_webhook_router, prefix=prefix)
app.include_router(subscriptions_router, prefix=prefix)
app.include_router(subscriptions_webhook_router, prefix=prefix)
app.include_router(site_builder_admin_router, prefix=prefix)
app.include_router(site_builder_public_router, prefix=prefix)
app.include_router(analytics_router, prefix=prefix)
app.include_router(reviews_router, prefix=prefix)


@app.get(f"{prefix}/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
