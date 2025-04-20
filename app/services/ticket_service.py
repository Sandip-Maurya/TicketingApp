# app/services/event_helpers.py

from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session
from app.database_setup.model import Ticket, Event

def get_unsold_ticket_status(db: Session) -> dict:
    now = datetime.now()

    # 1) find upcoming events
    upcoming = db.query(Event).filter(Event.event_datetime >= now).all()
    event_map = {e.id: e.name for e in upcoming}
    valid_ids = set(event_map)

    # 2) prepare result structure
    #    each entry: { event_name: { ticket_type: {count: int, price: float} } }
    result = defaultdict(lambda: defaultdict(lambda: {"count": 0, "price": None}))

    # 3) fetch all unsold tickets for those events
    tickets = db.query(Ticket).filter(
        Ticket.is_sold == False,
        Ticket.event_id.in_(valid_ids)
    ).all()

    # 4) tally them
    for t in tickets:
        ev_name = event_map[t.event_id]
        info = result[ev_name][t.ticket_type.value]
        info["count"] += 1
        # price will be same for all of that type—just overwrite to the same value
        info["price"] = t.price

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
