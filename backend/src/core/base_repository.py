from typing import Generic, TypeVar
from uuid import UUID

from sqlmodel import Session, SQLModel, select

from core.exceptions import NotFoundError, TenantIsolationError

T = TypeVar("T", bound=SQLModel)


class TenantScopedRepository(Generic[T]):
    """
    Repositorio base: SIEMPRE filtra por tenant_id (reglas A1, A3).
    No usar get_by_id sin tenant del TenancyContext.
    """

    model: type[T]

    def __init__(self, session: Session, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    def _tenant_column(self):
        col = getattr(self.model, "tenant_id", None)
        if col is None:
            raise TenantIsolationError()
        return col

    def get_by_id(self, resource_id: UUID) -> T:
        stmt = select(self.model).where(
            self.model.id == resource_id,
            self._tenant_column() == self.tenant_id,
        )
        row = self.session.exec(stmt).first()
        if row is None:
            raise NotFoundError(self.model.__name__)
        return row

    def get_by_id_optional(self, resource_id: UUID) -> T | None:
        stmt = select(self.model).where(
            self.model.id == resource_id,
            self._tenant_column() == self.tenant_id,
        )
        return self.session.exec(stmt).first()

    def list_all(self, *, offset: int = 0, limit: int = 100) -> list[T]:
        stmt = (
            select(self.model)
            .where(self._tenant_column() == self.tenant_id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    def add(self, entity: T) -> T:
        if getattr(entity, "tenant_id", None) != self.tenant_id:
            raise TenantIsolationError()
        self.session.add(entity)
        self.session.flush()
        return entity
