from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Tenant resuelto en servidor — no construir desde body del cliente (regla A2)."""

    tenant_id: UUID
    slug: str
    plan_code: str
    features: frozenset[str]

    def has_feature(self, code: str) -> bool:
        return code in self.features
