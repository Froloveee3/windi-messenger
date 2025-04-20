from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserRead


class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    participant_ids: List[int]

class GroupRead(GroupBase):
    id: int
    creator_id: Optional[int]
    participants: List[UserRead] = []
    
    model_config = ConfigDict(from_attributes=True)
