from typing import Optional
from datetime import datetime
from pydantic import ConfigDict, BaseModel


class MessageBase(BaseModel):
    text: str

class MessageCreate(MessageBase):
    chat_id: int
    sender_id: int
    client_msg_id: Optional[str] = None

class MessageRead(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    timestamp: datetime
    read: bool
    
    model_config = ConfigDict(from_attributes=True)
