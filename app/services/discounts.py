# app/services/discounts.py

from datetime import datetime
from typing import Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from app.database_setup.model import Discount, DiscountApplicability, Event

def get_best_discount(
    db: Session,
    event_id: int,
    ticket_type: str,
    quantity: int
) -> Optional[Discount]:
    today = datetime.now()

    # Step 1: Load all valid discounts and filter in Python
    discounts = db.query(Discount).filter(
        Discount.valid_till >= today,
        Discount.min_tickets <= quantity
    ).all()

    # Manual filtering since SQLite doesn't support JSON contains properly
    discounts = [d for d in discounts if event_id in d.applicable_events]

    applicable_discounts = []

    for d in discounts:
        if ticket_type == 'both':
            if d.applicable_ticket_types == DiscountApplicability.both:
                applicable_discounts.append(d)
        else:
            if (
                d.applicable_ticket_types.value == ticket_type
                or d.applicable_ticket_types == DiscountApplicability.both
            ):
                applicable_discounts.append(d)

    if applicable_discounts:
        return max(applicable_discounts, key=lambda d: d.percentage_off)

    return None


def get_all_active_discounts_grouped(db):
    today = datetime.now()
    discounts = db.query(Discount).filter(Discount.valid_till >= today).all()

    # Fetch event ID to name mapping
    event_map = {event.id: event.name for event in db.query(Event.id, Event.name).all()}

    result = defaultdict(lambda: defaultdict(list))
    for d in discounts:
        for event_id in d.applicable_events:
            event_name = event_map.get(event_id, f'Event {event_id}')
            result[event_name][d.applicable_ticket_types.value] = {
                'name': d.name,
                'percentage_off': d.percentage_off,
                'min_tickets': d.min_tickets,
                'valid_till': d.valid_till.strftime('%Y-%m-%d')
            }

    return result
