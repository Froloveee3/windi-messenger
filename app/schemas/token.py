from pydantic import BaseModel, ConfigDict
from typing import List


class TokenPayload(BaseModel):
    sub: str
    exp: int
    scopes: List[str] = []

    model_config = ConfigDict(from_attributes=True)
