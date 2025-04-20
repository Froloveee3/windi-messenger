from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.user import UserRead


class ChatBase(BaseModel):
    name: Optional[str] = None
    type: Literal["personal", "group"]

class ChatCreate(ChatBase):
    participant_ids: List[int]

    @model_validator(mode="after")
    def check_participants(cls, m):
        if m.type == "group":
            if len(m.participant_ids) < 2:
                raise ValueError("Group chat must have at least 2 participants")
            if not m.name:
                raise ValueError("Group chat must have a name")
        return m

class ChatRead(ChatBase):
    id: int
    participants: List[UserRead] = []
    
    model_config = ConfigDict(from_attributes=True)