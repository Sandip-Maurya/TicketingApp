# app/services/event_helpers.py

from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session
from app.database_setup.model import Ticket, Event

def get_unsold_ticket_status(db: Session) -> dict:
    now = datetime.now()

    # 1) Find upcoming events
    upcoming = db.query(Event).filter(Event.event_datetime >= now).all()
    event_map = {e.id: e.name for e in upcoming}
    valid_ids = set(event_map)

    # 2) Initialize result with default values for both ticket types
    result = {}
    for event in upcoming:
        result[event.name] = {
            'regular': {'count': 0, 'price': 0.0},
            'vip':     {'count': 0, 'price': 0.0},
        }

    # 3) Fetch unsold tickets
    tickets = db.query(Ticket).filter(
        Ticket.is_sold == False,
        Ticket.event_id.in_(valid_ids)
    ).all()

    # 4) Update result based on available unsold tickets
    for t in tickets:
        event_name = event_map[t.event_id]
        ticket_type = t.ticket_type.value
        result[event_name][ticket_type]['count'] += 1
        result[event_name][ticket_type]['price'] = t.price  # safe overwrite

    return result


def get_ticket_types(db: Session) -> list[dict]:
    events = db.query(Event).all()
    
    result = []
    for event in events:
        result.append({
            'event_name': event.name,
            'ticket_types': event.available_ticket_types
        })
    
    return result
