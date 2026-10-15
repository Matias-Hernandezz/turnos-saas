from uuid import UUID

from sqlmodel import Session, col, func, select

from core.exceptions import AppError, NotFoundError
from features.catalog.repository import ProfessionalRepository, ServiceRepository
from features.catalog.schemas import (
    ProfessionalCreate,
    ProfessionalRead,
    ProfessionalUpdate,
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)
from models.catalog import Professional, Service
from tenancy.context import TenantContext
from tenancy.plan_limits import PLAN_LIMITS


class CatalogService:
    def __init__(self, session: Session, tenant: TenantContext) -> None:
        self.session = session
        self.tenant = tenant
        self.services = ServiceRepository(session, tenant.tenant_id)
        self.professionals = ProfessionalRepository(session, tenant.tenant_id)

    def list_services(self) -> list[ServiceRead]:
        rows = self.services.list_all(limit=200)
        return [self._service_read(r) for r in rows]

    def list_active_services(self) -> list[ServiceRead]:
        rows = self.services.list_all(limit=200)
        return [self._service_read(r) for r in rows if r.is_active]

    def list_active_professionals(self) -> list[ProfessionalRead]:
        rows = self.professionals.list_all(limit=200)
        return [self._professional_read(r) for r in rows if r.is_active]

    def create_service(self, body: ServiceCreate) -> ServiceRead:
        entity = Service(
            tenant_id=self.tenant.tenant_id,
            name=body.name,
            duration_minutes=body.duration_minutes,
            price_cents=body.price_cents,
            is_active=body.is_active,
        )
        saved = self.services.add(entity)
        self.session.commit()
        self.session.refresh(saved)
        return self._service_read(saved)

    def update_service(self, service_id: UUID, body: ServiceUpdate) -> ServiceRead:
        entity = self.services.get_by_id(service_id)
        if body.name is not None:
            entity.name = body.name
        if body.duration_minutes is not None:
            entity.duration_minutes = body.duration_minutes
        if body.price_cents is not None:
            entity.price_cents = body.price_cents
        if body.is_active is not None:
            entity.is_active = body.is_active
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return self._service_read(entity)

    def delete_service(self, service_id: UUID) -> None:
        entity = self.services.get_by_id(service_id)
        self.session.delete(entity)
        self.session.commit()

    def list_professionals(self) -> list[ProfessionalRead]:
        rows = self.professionals.list_all(limit=200)
        return [self._professional_read(r) for r in rows]

    def create_professional(self, body: ProfessionalCreate) -> ProfessionalRead:
        self._enforce_professional_limit()
        entity = Professional(
            tenant_id=self.tenant.tenant_id,
            name=body.name,
            is_active=body.is_active,
        )
        saved = self.professionals.add(entity)
        self.session.commit()
        self.session.refresh(saved)
        return self._professional_read(saved)

    def update_professional(self, professional_id: UUID, body: ProfessionalUpdate) -> ProfessionalRead:
        entity = self.professionals.get_by_id(professional_id)
        if body.name is not None:
            entity.name = body.name
        if body.is_active is not None:
            entity.is_active = body.is_active
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return self._professional_read(entity)

    def delete_professional(self, professional_id: UUID) -> None:
        entity = self.professionals.get_by_id(professional_id)
        self.session.delete(entity)
        self.session.commit()

    def _enforce_professional_limit(self) -> None:
        limits = PLAN_LIMITS.get(self.tenant.plan_code, {})
        max_pros = limits.get("max_professionals")
        if max_pros is None:
            return
        count = self.session.exec(
            select(func.count(col(Professional.id))).where(
                Professional.tenant_id == self.tenant.tenant_id
            )
        ).one()
        if count >= max_pros:
            raise AppError(
                f"Plan allows at most {max_pros} professional(s)",
                code="plan_limit",
            )

    @staticmethod
    def _service_read(row: Service) -> ServiceRead:
        assert row.id is not None
        return ServiceRead(
            id=str(row.id),
            name=row.name,
            duration_minutes=row.duration_minutes,
            price_cents=row.price_cents,
            is_active=row.is_active,
        )

    @staticmethod
    def _professional_read(row: Professional) -> ProfessionalRead:
        assert row.id is not None
        return ProfessionalRead(id=str(row.id), name=row.name, is_active=row.is_active)
