# app/services/event_helpers.py

from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session
from app.database_setup.model import Ticket, Event

def get_unsold_ticket_status(db: Session) -> dict:
    now = datetime.now()
    result = defaultdict(lambda: defaultdict(int))

    # Fetch events whose event_datetime is in the future
    upcoming_events = db.query(Event).filter(
        Event.event_datetime >= now
    ).all()

    event_map = {e.id: e.name for e in upcoming_events}
    valid_event_ids = set(event_map.keys())

    # Get unsold tickets for those events
    tickets = db.query(Ticket).filter(
        Ticket.is_sold == False,
        Ticket.event_id.in_(valid_event_ids)
    ).all()

    for ticket in tickets:
        event_name = event_map[ticket.event_id]
        result[event_name][ticket.ticket_type.value] += 1

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
