
# # app/schemas/order_schemas.py

from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# incoming payload
class TicketOrder(BaseModel):
    regular: int = Field(..., ge = 0, json_schema_extra = {"example": 4} )
    vip: int      = Field(..., ge = 0, json_schema_extra = {"example": 2})


class CheckOfferRequest(BaseModel):
    event_id: int = 1
    tickets: TicketOrder

    model_config = ConfigDict(
        json_schema_extra = {
            'example': {
                'event_id': 1,
                'tickets': {'regular': 6, 'vip': 3}
            }
        }
    )

class OfferInfo(BaseModel):
    name: str
    percentage_off: float
    saving: float
    min_tickets: int              
    applicable_ticket_type: str   


class OrderCreate(BaseModel):
    event_id: int = 1
    tickets: TicketOrder
    user_name: str
    user_email: EmailStr

# alias so order_utils.OrderPayload still works
OrderPayload = OrderCreate

# outgoing per‐category detail
class TicketCategoryDetail(BaseModel):
    ticket_ids: List[int]
    count: int
    unit_price: float
    offer: Optional[str] = None
    discount_per_ticket: float
    final_price_per_ticket: float

class TicketsOut(BaseModel):
    regular: TicketCategoryDetail
    vip: TicketCategoryDetail


class UserOut(BaseModel):
    name: str
    email: EmailStr

class OrderTotal(BaseModel):
    before_discount: float
    savings: float
    after_discount: float

class OrderResponse(BaseModel):
    message: str
    order_id: int
    user: UserOut
    tickets: TicketsOut
    total: OrderTotal
    applied_offers: List[str]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'message': 'Your order was successful.',
                'order_id': 130,
                'user': {'name': 'Sandip', 'email': 'sandip@example.com'},
                'tickets': {
                    'regular': {
                        'ticket_ids': [449, 450, 451, 452, 453, 454],
                        'count': 6,
                        'unit_price': 1000,
                        'offer': 'Group Saver',
                        'discount_per_ticket': 100,
                        'final_price_per_ticket': 900
                    },
                    'vip': {
                        'ticket_ids': [932, 933, 934],
                        'count': 3,
                        'unit_price': 3000,
                        'offer': 'VIP Treat',
                        'discount_per_ticket': 450,
                        'final_price_per_ticket': 2550
                    }
                },
                'total': {
                    'before_discount': 15000,
                    'savings': 1950,
                    'after_discount': 13050
                },
                'applied_offers': ['Mega Combo']
            }
        }
    )
