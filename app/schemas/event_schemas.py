# app/schemas/event_schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    name: str
    venue: str
    event_datetime: datetime
    description: Optional[str] = None

class EventCreate(EventBase):
    ...

class EventUpdate(BaseModel):
    name: Optional[str] = None
    venue: Optional[str] = None
    event_datetime: Optional[datetime] = None
    description: Optional[str] = None

class EventOut(EventBase):
    id: int
    class Config:
        orm_mode = True
        
class EventResponse(BaseModel):
    message: str
    event: EventOut


class EventDeleteResponse(BaseModel):
    message: str
    id: int
    name: str