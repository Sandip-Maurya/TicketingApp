
# app/schemas/order_schemas.py

from pydantic import BaseModel, EmailStr, Field, conint
from typing import Annotated, Dict
from enum import Enum

TicketQty = Annotated[int, conint(ge=1)]  

class TicketType(str, Enum):
    regular = 'regular'
    vip     = 'vip'

class OrderPayload(BaseModel):
    event_id: int = 1
    tickets: Dict[TicketType, TicketQty] = Field(..., example={'regular': 5, 'vip': 3})
    user_name: str
    user_email: EmailStr

class CheckOfferRequest(BaseModel):
    event_id: int
    tickets: Dict[TicketType, TicketQty] = Field(..., example={'regular': 5, 'vip': 3})
