from typing import Annotated

from fastapi import Header


def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    return authorization[7:].strip()
