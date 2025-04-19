# app/schemas/event_schemas.py

from pydantic import BaseModel
from datetime import datetime

class EventOut(BaseModel):
    id: int
    name: str
    venue: str
    event_datetime: datetime
    description: str | None

    class Config:
        orm_mode = True
