# # app/api/orders.py

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database_setup.database import get_db
# from app.schemas.order_schemas import OrderPayload
# from app.services.order_service import process_order

# router = APIRouter()

# @router.post("/")
# def complete_order(payload: OrderPayload, db: Session = Depends(get_db)):
#     return process_order(payload, db)

''''''

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.order_schemas import OrderCreate, OrderResponse
from app.services.order_service import place_order as service_place_order
from app.database_setup.database import get_db

router = APIRouter()

@router.post(
    '/',
    response_model=OrderResponse,
    summary = 'Place an order',
    status_code=status.HTTP_201_CREATED
)
def place_order(
    payload: OrderCreate,
    db: Session = Depends(get_db)
) -> OrderResponse:
    return service_place_order(db, payload)
