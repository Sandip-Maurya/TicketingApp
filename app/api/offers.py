# app/api/offers.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database_setup.database import get_db
from app.services.discounts import get_all_active_discounts_grouped
from app.schemas.order_schemas import CheckOfferRequest
from app.services.offer_helpers import preview_best_offers


router = APIRouter()

@router.get('/all')
def show_all_offers(db: Session = Depends(get_db)):
    return get_all_active_discounts_grouped(db)

@router.post('/check-offers')
def check_offers(payload: CheckOfferRequest, db: Session = Depends(get_db)):
    return preview_best_offers(payload, db)
