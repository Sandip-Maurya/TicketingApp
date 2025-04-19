# app/services/offer_helpers.py

from sqlalchemy.orm import Session
from app.schemas.order_schemas import CheckOfferRequest
from app.database_setup.model import Ticket
from app.services.order_logic import get_best_discount_strategy

def preview_best_offers(payload: CheckOfferRequest, db: Session) -> dict:
    all_tickets = []

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
                'available': False
            }

        all_tickets.extend(tickets)

    if not all_tickets:
        return {'message': 'No valid ticket request found.', 'available': False}

    discounts_applied, price_after_discount, strategy = get_best_discount_strategy(
        db,
        payload.event_id,
        all_tickets
    )

    return {
        'message': 'Offers preview generated successfully.',
        'total_price': sum(t.price for t in all_tickets),
        'price_after_discount': price_after_discount,
        'discount_applied': [
            {'id': d.id, 'name': d.name, 'type': d.applicable_ticket_types.value}
            for d in discounts_applied
        ],
        'strategy_used': strategy,
        'available': True
    }
