# app/api/orders.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database_setup.database import get_db
from app.schemas.order_schemas import OrderPayload
from app.services.orders import process_order

router = APIRouter()

@router.post("/")
def complete_order(payload: OrderPayload, db: Session = Depends(get_db)):
    return process_order(payload, db)
