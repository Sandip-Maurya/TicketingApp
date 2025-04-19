# app/services/offers_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from collections import defaultdict
from app.database_setup.model import Ticket
from app.schemas.order_schemas import CheckOfferRequest, OfferInfo
from app.services.discount_strategy import get_best_discount_strategy, get_best_discount
from app.services.order_utils import validate_event 


def preview_offers(payload: CheckOfferRequest, db: Session) -> dict:

    # Step 0: Validate event
    event = validate_event(payload.event_id, db)

    # Step 1: Fetch tickets based on availability
    selected_tickets = []

    for ticket_type, qty in payload.tickets.items():
        if qty <= 0:
            continue
        tickets = db.query(Ticket).filter(
            Ticket.event_id == payload.event_id,
            Ticket.ticket_type == ticket_type,
            Ticket.is_sold == False
        ).limit(qty).all()

        if len(tickets) < qty:
            return {
                'message': f'Only {len(tickets)} {ticket_type.value} tickets available',
                'tickets_available': False
            }

        selected_tickets.extend(tickets)

    if not selected_tickets:
        raise HTTPException(status_code=400, detail='No valid tickets requested.')

    total_price = sum(t.price for t in selected_tickets)

    # Step 2: Get discount strategy result
    discounts_applied, price_after_discount, strategy = get_best_discount_strategy(
        db, payload.event_id, selected_tickets
    )

    # Step 3: Get all possible offers

    all_applicable_discounts = []
    seen = set()

    # Group by ticket type
    grouped = defaultdict(list)
    for t in selected_tickets:
        grouped[t.ticket_type.value].append(t)

    # Evaluate per ticket type
    for ticket_type, group in grouped.items():
        discount = get_best_discount(db, payload.event_id, ticket_type, len(group))
        if discount and discount.id not in seen:
            seen.add(discount.id)
            type_total = sum(t.price for t in group)
            saving = type_total * discount.percentage_off / 100
            all_applicable_discounts.append(
                OfferInfo(
                    name=discount.name,
                    percentage_off=discount.percentage_off,
                    saving=round(saving, 2)
                )
            )

    # Evaluate combined
    combo_discount = get_best_discount(db, payload.event_id, 'both', len(selected_tickets))
    if combo_discount and combo_discount.id not in seen:
        combo_total = total_price
        saving = combo_total * combo_discount.percentage_off / 100
        all_applicable_discounts.append(
            OfferInfo(
                name=combo_discount.name,
                percentage_off=combo_discount.percentage_off,
                saving=round(saving, 2)
            )
        )

    # Step 4: Response
    best = max(all_applicable_discounts, key=lambda o: o.saving, default=None)

    return {
        'message': 'Here is the best offer for you.' if best else 'No active offers, but feel free to explore more tickets!',
        'your_input': {
            'event_id': payload.event_id,
            'tickets': {k.value: v for k, v in payload.tickets.items()}
        },
        'applicable_discounts': all_applicable_discounts,
        'applied_discounts': best.name if best else None,
        'total_price': total_price,
        'price_after_discount': price_after_discount,
        'tickets_available': True
    }
