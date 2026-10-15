from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session

from core.database import engine


class UnitOfWork:
    def __init__(self) -> None:
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork not started")
        return self._session

    def __enter__(self) -> "UnitOfWork":
        self._session = Session(engine)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._session is None:
            return
        if exc_type is None:
            self._session.commit()
        else:
            self._session.rollback()
        self._session.close()
        self._session = None


@contextmanager
def unit_of_work() -> Generator[Session, None, None]:
    with UnitOfWork() as uow:
        yield uow.session
