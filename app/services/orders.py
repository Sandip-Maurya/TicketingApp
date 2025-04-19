# app/services/orders.py

from sqlalchemy.orm import Session
from app.schemas.order_schemas import OrderPayload
from app.services.order_helpers import validate_event, reserve_tickets_by_type, create_order_record
from app.services.order_logic import get_best_discount_strategy
from app.schemas.order_schemas import OrderPayload
from sqlalchemy.orm import Session


def process_order(payload: OrderPayload, db: Session) -> dict:
    # 1. Validate event
    event = validate_event(payload.event_id, db)

    # 2. Reserve tickets (raises error if not enough)
    selected_tickets = reserve_tickets_by_type(
        db,
        payload.event_id,
        payload.tickets,
        payload.user_email
    )

    ticket_ids = [t.id for t in selected_tickets]
    total_price = sum(t.price for t in selected_tickets)

    # 3. Get best discount strategy
    discounts_applied, price_after_discount, strategy = get_best_discount_strategy(
        db,
        payload.event_id,
        selected_tickets
    )

    # 4. Save order
    applied_discount_ids = [d.id for d in discounts_applied] if discounts_applied else []

    order = create_order_record(
        payload=payload,
        selected_ticket_ids=ticket_ids,
        total_price=total_price,
        price_after_discount=price_after_discount,
        discount_ids=applied_discount_ids,
        db=db
    )

    return {
        "message": "Order created successfully.",
        "order_id": order.id,
        "ticket_ids": ticket_ids,
        "total_price": total_price,
        "price_after_discount": price_after_discount,
        "discount_applied": [
            {"id": d.id, "name": d.name, "type": d.applicable_ticket_types.value}
            for d in discounts_applied
        ],
        "strategy_used": strategy
    }
