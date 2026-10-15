"""Dos sesiones DB compitiendo por el mismo slot (SQLite no soporta hilos en un pool)."""

from datetime import time
from uuid import uuid4

import pytest
from sqlmodel import Session

from core.database import engine
from core.exceptions import AppError
from features.booking.schemas import BookingCreatePublic
from features.booking.service import BookingService
from models.availability import WorkingHours
from models.catalog import Professional, Service
from models.tenant import Tenant
from tenancy.context import TenantContext
from tenancy.plan_seed import ensure_default_plans


def _seed_tenant(session: Session) -> tuple[TenantContext, Service, Professional, str]:
    ensure_default_plans(session)
    slug = f"conc-{uuid4().hex[:8]}"
    tenant = Tenant(slug=slug, name="Conc", plan_code="basic", feature_flags=[])
    session.add(tenant)
    session.flush()
    assert tenant.id is not None
    service = Service(
        tenant_id=tenant.id,
        name="Corte",
        duration_minutes=30,
        price_cents=1000,
    )
    pro = Professional(tenant_id=tenant.id, name="Pro")
    session.add(service)
    session.add(pro)
    session.flush()
    session.add(
        WorkingHours(
            tenant_id=tenant.id,
            professional_id=pro.id,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
    )
    session.commit()
    session.refresh(service)
    session.refresh(pro)
    assert service.id is not None and pro.id is not None
    ctx = TenantContext(
        tenant_id=tenant.id,
        slug=slug,
        plan_code="basic",
        features=frozenset(),
    )
    return ctx, service, pro, "2026-06-01T09:00:00"


def test_two_db_sessions_same_slot_second_rejected():
    with Session(engine) as session:
        ctx, service, pro, starts_at = _seed_tenant(session)

    body = BookingCreatePublic(
        service_id=str(service.id),
        professional_id=str(pro.id),
        starts_at=starts_at,
        customer_name="Primero",
        customer_phone="+541100000001",
    )

    with Session(engine) as first_session:
        BookingService(first_session, ctx).create_public_hold(body)

    body.customer_name = "Segundo"
    body.customer_phone = "+541100000002"
    with Session(engine) as second_session:
        with pytest.raises(AppError) as err:
            BookingService(second_session, ctx).create_public_hold(body)
        assert err.value.code == "slot_unavailable"
