
# app/schemas/order_schemas.py

from pydantic import BaseModel, EmailStr, Field, conint
from typing import Annotated, Dict, Optional, List
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

class OfferInfo(BaseModel):
    name: str
    percentage_off: float
    saving: float

class OfferCheckResponse(BaseModel):
    message: str
    your_input: dict
    applicable_discounts: List[OfferInfo]
    applied_discounts: Optional[str] = None
    total_price: float
    price_after_discount: float
    tickets_available: bool