# app/services/order_service.py

from collections import defaultdict
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.order_schemas import OrderPayload
from app.services.order_utils import validate_event, reserve_tickets_by_type, create_order_record
from app.services.discount_strategy import get_best_discount_strategy

def process_order(payload: OrderPayload, db: Session) -> dict:

    total_requested = sum(payload.tickets.values())
    if total_requested <= 0:
        raise HTTPException(
            status_code=422,
            detail='You must request at least one ticket of any type.'
        )


    # 1. Validate event
    validate_event(payload.event_id, db)

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
    order = create_order_record(
        payload=payload,
        selected_ticket_ids=ticket_ids,
        total_price=total_price,
        price_after_discount=price_after_discount,
        discount_ids=[d.id for d in discounts_applied],
        db=db
    )

    # 5. Compute saved_amount per discount
    #    First, group ticket‑prices by ticket_type
    group_totals = defaultdict(float)
    for t in selected_tickets:
        group_totals[t.ticket_type.value] += t.price

    response_discounts = []
    if strategy == 'combined':
        # combined discount applies to the whole basket
        for d in discounts_applied:
            saved = total_price * d.percentage_off / 100
            response_discounts.append({
                'name': d.name,
                'applicable_ticket_types': d.applicable_ticket_types.value,
                'percentage_off': d.percentage_off,
                'saved_amount': round(saved, 2),
            })
    else:
        # separate discounts apply per ticket type
        for d in discounts_applied:
            ttype = d.applicable_ticket_types.value
            saved = group_totals.get(ttype, 0.0) * d.percentage_off / 100
            response_discounts.append({
                'name': d.name,
                'applicable_ticket_types': ttype,
                'percentage_off': d.percentage_off,
                'saved_amount': round(saved, 2),
            })

    return {
        'message': 'Your order is successfully.',
        'order_id': order.id,
        'ticket_ids': ticket_ids,
        'total_price': total_price,
        'price_after_discount': price_after_discount,
        'savings': round(total_price - price_after_discount, 2),
        'discount_applied': response_discounts
    }
