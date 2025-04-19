# app/schema/order_schemas.py

from pydantic import BaseModel, Field, EmailStr

class OrderPayload(BaseModel):
    event_id: int = Field(ge=1)
    quantity: int = Field(ge=1)
    user_name: str
    user_email: EmailStr
