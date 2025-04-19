# app/services/discount_engine.py

from datetime import datetime
from collections import defaultdict
from app.database_setup.model import Discount, Event

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
