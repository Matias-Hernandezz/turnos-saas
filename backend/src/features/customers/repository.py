from core.base_repository import TenantScopedRepository
from models.customer import Customer


class CustomerRepository(TenantScopedRepository[Customer]):
    model = Customer
