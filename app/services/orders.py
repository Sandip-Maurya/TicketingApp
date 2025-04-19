# app/services/orders.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.discounts import get_best_discount
from app.schemas.order_schemas import OrderPayload
from app.services.order_helpers import (
    validate_event,
    get_available_tickets,
    select_and_reserve_tickets,
    apply_discount,
    create_order_record
)


def process_order(payload: OrderPayload, db: Session) -> dict:
    event = validate_event(payload.event_id, db)
    tickets = get_available_tickets(payload.event_id, db)

    if payload.quantity > len(tickets):
        raise HTTPException(status_code=404, detail=f"Only {len(tickets)} tickets available")

    selected_tickets, ticket_ids = select_and_reserve_tickets(tickets, payload.quantity, payload.user_email, db)
    total_price = sum(ticket.price for ticket in selected_tickets)
    ticket_type = selected_tickets[0].ticket_type.value

    discount, price_after_discount = apply_discount(db, event.id, ticket_type, payload.quantity, total_price)

    order = create_order_record(
        payload=payload,
        selected_ticket_ids=ticket_ids,
        total_price=total_price,
        price_after_discount=price_after_discount,
        discount=discount,
        db=db
    )

    return {
        "order_id": order.id,
        "ticket_ids": ticket_ids,
        "discount_applied": discount.name if discount else None
    }
