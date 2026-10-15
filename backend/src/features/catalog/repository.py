from core.base_repository import TenantScopedRepository
from models.catalog import Professional, Service


class ServiceRepository(TenantScopedRepository[Service]):
    model = Service


class ProfessionalRepository(TenantScopedRepository[Professional]):
    model = Professional
