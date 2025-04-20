# app/services/offers_service.py

from collections import defaultdict
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database_setup.model import Ticket
from app.schemas.order_schemas import CheckOfferRequest, OfferInfo
from app.services.discount_strategy import get_best_discount_strategy, get_best_discount
from app.services.order_utils import validate_event


def preview_offers(payload: CheckOfferRequest, db: Session) -> dict:
    # Step 0: Validate event
    validate_event(payload.event_id, db)

    # Step 1: Pull requested tickets & ensure availability
    selected_tickets = []
    for ticket_type, qty in payload.tickets.items():
        if qty <= 0:
            continue
        batch = (
            db.query(Ticket)
            .filter(
                Ticket.event_id == payload.event_id,
                Ticket.ticket_type == ticket_type,
                Ticket.is_sold == False,
            )
            .limit(qty)
            .all()
        )
        if len(batch) < qty:
            return {
                'message': f'Only {len(batch)} {ticket_type.value} tickets available',
                'tickets_available': False
            }
        selected_tickets.extend(batch)

    if not selected_tickets:
        raise HTTPException(status_code=400, detail='No valid tickets requested.')

    total_price = sum(t.price for t in selected_tickets)

    # Step 2: Compute best‐discount Strategy
    discounts_applied, price_after_discount, strategy = get_best_discount_strategy(
        db, payload.event_id, selected_tickets
    )

    # Step 3: Build ticket_prices map
    grouped = defaultdict(list)
    for t in selected_tickets:
        grouped[t.ticket_type.value].append(t)
    ticket_prices = {tt: grp[0].price for tt, grp in grouped.items()}

    # Step 4: Gather every applicable discount
    all_applicable_discounts = []
    
    seen = set()

    # a) Per‐type discounts
    for tt, grp in grouped.items():
        qty = len(grp)
        disc = get_best_discount(db, payload.event_id, tt, qty)
        if disc and disc.id not in seen:
            seen.add(disc.id)
            group_total = sum(t.price for t in grp)
            saving = group_total * disc.percentage_off / 100
            all_applicable_discounts.append(OfferInfo(
                name=disc.name,
                percentage_off=disc.percentage_off,
                saving=round(saving, 2),
                price=grp[0].price,
                min_tickets=disc.min_tickets,
                applicable_ticket_type=tt,
            ))

    # b) Combined discount
    combo = get_best_discount(db, payload.event_id, 'both', len(selected_tickets))
    if combo and combo.id not in seen:
        saving = total_price * combo.percentage_off / 100
        # for combined, price per‐ticket isn't meaningful, set to 0 or omit
        all_applicable_discounts.append(OfferInfo(
            name=combo.name,
            percentage_off=combo.percentage_off,
            saving=round(saving, 2),
            price=0.0,
            min_tickets=combo.min_tickets,
            applicable_ticket_type='both',
        ))

    # Step 5: Build the applied_discounts list
    applied_discounts = []
    for disc in discounts_applied:
        if strategy == 'combined':
            tt = 'both'
            grp_total = total_price
            grp_after = price_after_discount
        else:
            tt = disc.applicable_ticket_types.value
            grp_total = sum(t.price for t in grouped[tt])
            grp_after = round(grp_total * (1 - disc.percentage_off / 100), 2)

        applied_discounts.append({
            'ticket_type': tt,
            'name': disc.name,
            'percentage_off': disc.percentage_off,
            'min_tickets': disc.min_tickets,
            'saving': round(grp_total * disc.percentage_off / 100, 2),
            'total_price': grp_total,
            'price_after_discount': grp_after,
        })

    return {
        'message': 'Here is the best offer for you.' if applied_discounts else
                   'No active offers; buy more tickets to unlock savings!',
        'your_input': {
            'event_id': payload.event_id,
            'tickets': {k.value: v for k, v in payload.tickets.items()}
        },
        'ticket_prices': ticket_prices,
        'applicable_discounts': all_applicable_discounts,
        'applied_discounts': applied_discounts,
        'total_price': total_price,
        'price_after_discount': price_after_discount,
        'tickets_available': True
    }
