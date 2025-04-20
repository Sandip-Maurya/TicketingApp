# app/api/orders.py

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
from app.database_setup.model import Order

router = APIRouter()

# Endpoint to reserve tickets (initiates a transaction)
@router.post(
    '/reserve',
    response_model = OrderResponse,
    status_code = status.HTTP_201_CREATED,
    summary = 'Reserve tickets'
)
def api_reserve(payload: OrderReserveIn, db: Session = Depends(get_db)):
    try:
        # Transaction ensures atomicity for order reservation
        with db.begin():
            result = reserve_order(db, payload)
        return result
    except HTTPException:
        raise  # propagate HTTP exceptions directly
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f'Reservation failed: {str(e)}'
        )

# Confirm a previously reserved order
@router.post(
    '/{order_id}/confirm',
    response_model = OrderResponse,
    status_code = status.HTTP_200_OK,
    summary = 'Confirm a reserved order'
)
def api_confirm(order_id: int, db: Session = Depends(get_db)):
    return confirm_order(db, order_id)

# Cancel a reserved order
@router.post(
    '/{order_id}/cancel',
    response_model = OrderResponse,
    status_code = status.HTTP_200_OK,
    summary = 'Cancel a reserved order'
)
def api_cancel(order_id: int, db: Session = Depends(get_db)):
    return cancel_order(db, order_id)

# Fetch details of a specific order
@router.get(
    '/{order_id}',
    response_model = dict,
    summary = 'Fetch an order'
)
def api_get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Order not found')

    return {
        'id': order.id,
        'status': order.status.value,
        'tickets': order.sold_tickets_ids
    }
