from core.base_repository import TenantScopedRepository
from models.page_config import PageConfig


class PageConfigRepository(TenantScopedRepository[PageConfig]):
    model = PageConfig
