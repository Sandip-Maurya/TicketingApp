# ./app/database_setup/seed_data.py

from app.database_setup.database import SessionLocal
from app.database_setup.model import Event, Ticket, TicketTypes
from app.database_setup.config import EVENTS

def seed_events_and_tickets_table():
    db = SessionLocal()
    try:
        for event_data in EVENTS:
            # Check if event already exists
            existing = db.query(Event).filter(Event.name == event_data['name']).first()
            if existing:
                print(f"Event: {existing.name} already added.")
                continue

            # Create and insert Event
            event = Event(
                name=event_data['name'],
                venue=event_data['venue'],
                event_datetime=event_data['event_datetime'],
                description=event_data['description'],
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            print(f"Added event: {event.name}")

            # Create and insert Tickets
            for ticket_type, ticket_info in event_data["tickets"].items():
                for _ in range(ticket_info["count"]):
                    ticket = Ticket(
                        event_id=event.id,
                        price=ticket_info["price"],
                        ticket_type=TicketTypes(ticket_type),
                        is_sold=False
                    )
                    db.add(ticket)
            db.commit()
            print(f"Added ticket data for the event: {event.name}")

    finally:
        db.close()

if __name__ == '__main__':
    seed_events_and_tickets_table()
