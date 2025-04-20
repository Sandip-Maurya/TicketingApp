# app/schemas/offer_schemas.py

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

class TicketCounts(BaseModel):
    regular: int = Field(..., ge = 0, json_schema_extra = {"example": 6} )
    vip: int      = Field(..., ge = 0, json_schema_extra = {"example": 3})
    

class CheckOfferRequest(BaseModel):
    event_id: int  = 1
    tickets: TicketCounts
    model_config = ConfigDict(
        json_schema_extra = {
            'example': {
                'event_id': 1,
                'tickets': { 'regular': 6, 'vip': 3 }
            }
        }
    )


class Offer(BaseModel):
    name: str
    percentage_off: float
    saving: float
    discount_per_ticket: float
    final_price_per_ticket: Optional[float]

class CategoryOffer(BaseModel):
    count: int
    unit_price: Optional[float]
    eligible_offers: List[Offer]
    selected_offer: Offer

class OfferTotal(BaseModel):
    before: float
    savings: float
    after: float

class OffersResponse(BaseModel):
    message: str
    tickets: Dict[Literal['regular','vip','combined'], CategoryOffer]
    total: OfferTotal
