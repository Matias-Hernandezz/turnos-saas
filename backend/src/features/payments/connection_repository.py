from sqlmodel import select

from core.base_repository import TenantScopedRepository
from models.payment import MercadoPagoConnection


class MercadoPagoConnectionRepository(TenantScopedRepository[MercadoPagoConnection]):
    model = MercadoPagoConnection

    def get_active(self) -> MercadoPagoConnection | None:
        stmt = select(MercadoPagoConnection).where(
            MercadoPagoConnection.tenant_id == self.tenant_id,
            MercadoPagoConnection.is_active.is_(True),
        )
        return self.session.exec(stmt).first()
