# app/admin/services/events_service.py

from typing import Optional
from sqlalchemy.orm import Session

from app.database_setup.model import Event
from app.schemas.event_schemas import EventCreate, EventUpdate

def create_event(db: Session, payload: EventCreate) -> Event:
    new_event = Event(
        name=payload.name,
        venue=payload.venue,
        event_datetime=payload.event_datetime,
        description=payload.description,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def update_event(db: Session, event_id: int, payload: EventUpdate) -> Optional[Event]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    # only update the fields provided
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event_id: int) -> Optional[Event]:

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    # capture its data, then delete
    db.delete(event)
    db.commit()
    return event
