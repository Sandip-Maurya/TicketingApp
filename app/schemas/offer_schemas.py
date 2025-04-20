# from typing import List, Literal, Dict
# from pydantic import BaseModel, Field


# class TicketCounts(BaseModel):
#     regular: int = Field(..., example=6)
#     vip: int      = Field(..., example=3)


# class CheckOfferRequest(BaseModel):
#     event_id: int         = Field(..., example=1)
#     tickets: TicketCounts

#     class Config:
#         schema_extra = {
#             'example': {
#                 'event_id': 1,
#                 'tickets': { 'regular': 6, 'vip': 3 }
#             }
#         }


# class Offer(BaseModel):
#     name: str
#     percentage_off: float
#     saving: float
#     discount_per_ticket: float
#     final_price_per_ticket: float


# class CategoryOffer(BaseModel):
#     count: int
#     unit_price: float
#     eligible_offers: List[Offer]
#     selected_offer: Offer


# class OfferTotal(BaseModel):
#     before: float
#     savings: float
#     after: float


# class OffersResponse(BaseModel):
#     message: str
#     tickets: Dict[Literal['regular', 'vip'], CategoryOffer]
#     total: OfferTotal

''''''

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

# class CheckOfferRequest(BaseModel):
#     event_id: int
#     tickets: Dict[Literal['regular','vip'], int]

class TicketCounts(BaseModel):
    regular: int = Field(..., example=6)
    vip: int      = Field(..., example=3)


class CheckOfferRequest(BaseModel):
    event_id: int  = Field(..., example=1)
    tickets: TicketCounts

    class Config:
        schema_extra = {
            'example': {
                'event_id': 1,
                'tickets': { 'regular': 6, 'vip': 3 }
            }
        }


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
