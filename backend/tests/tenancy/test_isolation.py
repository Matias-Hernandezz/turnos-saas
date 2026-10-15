from uuid import uuid4

import pytest

from core.exceptions import NotFoundError, TenantIsolationError
from features.catalog.repository import ServiceRepository
from models.catalog import Service
from models.tenant import Tenant


def _tenant(slug: str) -> Tenant:
    return Tenant(slug=slug, name=slug.title(), plan_code="basic")


def test_repository_get_by_id_respects_tenant(session):
    t1 = _tenant("uno")
    t2 = _tenant("dos")
    session.add(t1)
    session.add(t2)
    session.commit()
    session.refresh(t1)
    session.refresh(t2)

    assert t1.id is not None and t2.id is not None

    service = Service(
        tenant_id=t1.id,
        name="Corte",
        duration_minutes=30,
        price_cents=1000,
    )
    session.add(service)
    session.commit()
    session.refresh(service)
    assert service.id is not None

    repo_t1 = ServiceRepository(session, t1.id)
    found = repo_t1.get_by_id(service.id)
    assert found.name == "Corte"

    repo_t2 = ServiceRepository(session, t2.id)
    with pytest.raises(NotFoundError):
        repo_t2.get_by_id(service.id)


def test_repository_add_rejects_wrong_tenant_id(session):
    t1 = _tenant("uno")
    session.add(t1)
    session.commit()
    session.refresh(t1)
    assert t1.id is not None

    other = uuid4()
    service = Service(tenant_id=other, name="X", duration_minutes=30)
    repo = ServiceRepository(session, t1.id)
    with pytest.raises(TenantIsolationError):
        repo.add(service)
