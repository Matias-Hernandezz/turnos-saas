from pydantic import BaseModel


class CustomerRead(BaseModel):
    id: str
    full_name: str
