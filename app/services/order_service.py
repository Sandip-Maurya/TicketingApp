# app/services/order_service.py

# app/services/order_service.py

from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database_setup.model import Order, Ticket, OrderStatus
from app.schemas.order_schemas import OrderReserveIn, OrderResponse
from app.services.order_utils import validate_event, reserve_tickets_by_type
from app.services.order_utils import create_order_record
from app.services.discount_strategy import get_best_discount_strategy
from app.services.response_builders import build_order_response

def place_order(db: Session, payload: OrderReserveIn) -> OrderResponse:
    # 1. Ensure event exists
    validate_event(payload.event_id, db)

    # 2. Reserve tickets (marks them is_reserved=True)
    reserved: List[Ticket] = reserve_tickets_by_type(
        db,
        payload.event_id,
        payload.tickets.model_dump(),  # {'regular': n, 'vip': m}
        payload.user_email
    )
    if not reserved:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please select at least one ticket."
        )

    # 3. Compute discounts before persisting
    discounts_used, final_total, _strategy = get_best_discount_strategy(
        db, payload.event_id, reserved
    )
    total_before = sum(t.price for t in reserved)

    # 4. Persist the order record (status=reserved)
    order = create_order_record(
        payload,
        [t.id for t in reserved],
        total_before,
        final_total,
        [d.id for d in discounts_used],
        db
    )

    # 5. Build and return the uniform response
    return build_order_response(
        db,
        order,
        reserved,
        message=(
            "Your order is reserved. "
            "Please use the confirm or cancel route to finalize or release your reservation."
        )
    )

def confirm_order(db: Session, order_id: int) -> OrderResponse:
    # 1. Load & validate
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.status is not OrderStatus.reserved:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Order must be reserved to confirm (current: {order.status.value})"
        )

    # 2. Fetch the reserved tickets
    tickets = (
        db.query(Ticket)
          .filter(Ticket.id.in_(order.sold_tickets_ids))
          .with_for_update()
          .all()
    )
    if not tickets:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "No tickets found for this order"
        )

    # 3. Flip flags: clear reservation, mark sold
    for t in tickets:
        if not t.is_reserved:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Ticket {t.id} is not reserved."
            )
        t.is_reserved = False
        t.is_sold     = True
        db.add(t)

    # 4. Update the order status
    order.status = OrderStatus.confirmed
    db.add(order)
    db.flush()

    # 5. Build and return the uniform response
    return build_order_response(db, order, tickets, message="Order confirmed.")

def cancel_order(db: Session, order_id: int) -> OrderResponse:
    # 1. Load & validate
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.status is not OrderStatus.reserved:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Order must be reserved to cancel (current: {order.status.value})"
        )

    # 2. Fetch the reserved tickets
    tickets = db.query(Ticket).filter(Ticket.id.in_(order.sold_tickets_ids)).all()
    if not tickets:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "No tickets found for this order"
        )

    # 3. Release reservations
    for t in tickets:
        t.is_reserved = False
        db.add(t)

    # 4. Update the order status
    order.status = OrderStatus.cancelled
    db.add(order)
    db.flush()

    # 5. Build and return the uniform response
    return build_order_response(
        db,
        order,
        tickets,
        message="Order cancelled. Your holds have been released."
    )
