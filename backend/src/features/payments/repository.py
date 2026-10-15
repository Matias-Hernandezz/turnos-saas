from core.base_repository import TenantScopedRepository
from models.payment import Payment


class PaymentRepository(TenantScopedRepository[Payment]):
    model = Payment
