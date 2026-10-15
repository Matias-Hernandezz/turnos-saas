from core.base_repository import TenantScopedRepository
from models.availability import TimeOff


class TimeOffRepository(TenantScopedRepository[TimeOff]):
    model = TimeOff
