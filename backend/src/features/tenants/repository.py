from sqlmodel import Session, select

from models.tenant import Tenant


class TenantRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self.session.exec(select(Tenant).where(Tenant.slug == slug)).first()
