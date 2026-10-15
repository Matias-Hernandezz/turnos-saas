from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from core.config import get_settings

settings = get_settings()

_engine_kwargs: dict = {
    "echo": settings.app_debug,
    "pool_pre_ping": True,
}
if settings.database_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    if settings.database_url in ("sqlite://", "sqlite:///:memory:"):
        _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.database_url, **_engine_kwargs)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
