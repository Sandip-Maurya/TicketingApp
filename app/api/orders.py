
# # app/api/orders.py


# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.schemas.order_schemas import OrderCreate, OrderResponse
# from app.services.order_service import place_order as service_place_order
# from app.database_setup.database import get_db

# router = APIRouter()

# @router.post(
#     '/',
#     response_model=OrderResponse,
#     summary = 'Place an order',
#     status_code=status.HTTP_201_CREATED
# )
# def place_order(
#     payload: OrderCreate,
#     db: Session = Depends(get_db)
# ) -> OrderResponse:
#     return service_place_order(db, payload)

''''''

# app/api/orders.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.order_schemas import (
    OrderReserveIn, OrderResponse
)
from app.services.order_service import (
    place_order as reserve_order,
    confirm_order,
    cancel_order
)
from app.database_setup.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/reserve",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve tickets"
)
def api_reserve(payload: OrderReserveIn, db: Session = Depends(get_db)):
    try:
        # BEGIN transaction: all flushes/updates inside place_order will be committed
        with db.begin():
            result = reserve_order(db, payload)
        return result

    except HTTPException:
        # propagate your validation errors
        raise
    except Exception as e:
        logger.exception("Failed to reserve tickets")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reservation failed: {str(e)}"
        )


@router.post(
    "/{order_id}/confirm",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm a reserved order"
)
def api_confirm(
    order_id: int,
    db: Session = Depends(get_db)
):
    return confirm_order(db, order_id)

@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a reserved order"
)
def api_cancel(
    order_id: int,
    db: Session = Depends(get_db)
):
    return cancel_order(db, order_id)


# debug
from app.database_setup.model import Order

@router.get(
    "/{order_id}",
    response_model=dict,  # you can refine this later
    summary="Fetch an order (debug only)"
)
def api_get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return {
        "id": order.id,
        "status": order.status.value,
        "tickets": order.sold_tickets_ids
    }