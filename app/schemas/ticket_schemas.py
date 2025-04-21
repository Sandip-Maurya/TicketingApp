# app/schemas/ticket_schemas.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.database_setup.model import TicketTypes

class TicketCreate(BaseModel):
    ticket_type: TicketTypes   # accept enum
    price: float
    quantity: int

class TicketOut(BaseModel):
    id: int
    event_id: int
    ticket_type: TicketTypes
    price: float
    is_sold: bool

    model_config = ConfigDict(from_attributes=True)        


class TicketSummary(BaseModel):
    price: float
    count: int

class TicketsAddResponse(BaseModel):
    message: str
    event_id: int
    regular: Optional[TicketSummary] = None
    vip:     Optional[TicketSummary] = None


class TicketDelete(BaseModel):
    ticket_type: TicketTypes
    count: int


class TicketsDeleteResponse(BaseModel):
    message: str
    event_id: int
    regular: Optional[TicketSummary] = None
    vip:     Optional[TicketSummary] = None


class TicketDetail(BaseModel):
    count: int
    price: float

class EventUnsoldTickets(BaseModel):
    event_name: str
    regular: TicketDetail
    vip: TicketDetail

class EventTicketTypes(BaseModel):
    event_name: str
    ticket_types: List[str]
