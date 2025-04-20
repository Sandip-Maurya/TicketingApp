# # app/api/offers.py

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database_setup.database import get_db
# from app.services.get_all_discounts import get_all_active_discounts_grouped
# from app.schemas.order_schemas import CheckOfferRequest
# from app.services.offers_service import preview_offers

# router = APIRouter()

# @router.get('/all')
# def show_all_offers(db: Session = Depends(get_db)):
#     return get_all_active_discounts_grouped(db)

# @router.post('/check-offers')
# def check_offers(payload: CheckOfferRequest, db: Session = Depends(get_db)):
#     return preview_offers(payload, db)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.offer_schemas import CheckOfferRequest, OffersResponse
from app.services.offers_service import check_offers
from app.services.get_all_discounts import get_all_active_discounts_grouped
from app.database_setup.database import get_db

router = APIRouter()

@router.post(
    '/check-offers',
    response_model=OffersResponse
)
def offers_check(
    payload: CheckOfferRequest,
    db: Session = Depends(get_db)
) -> OffersResponse:
    return check_offers(db, payload)

@router.get('/all')
def show_all_offers(db: Session = Depends(get_db)):
    return get_all_active_discounts_grouped(db)
