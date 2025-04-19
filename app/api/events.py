# app/api/events.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database_setup.database import get_db
from app.database_setup.model import Event, Ticket
from fastapi import Query

router = APIRouter()

@router.get("/")
def get_all_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event for id {event_id} not found")
    return event

@router.get("/{event_id}/tickets")
def get_tickets(event_id: int, db: Session = Depends(get_db), limit: int = Query(default=10, ge=1)):
    tickets = db.query(Ticket).filter(Ticket.event_id == event_id, Ticket.is_sold == False).all()
    if not tickets:
        raise HTTPException(status_code=404, detail=f"Tickets not available for event_id={event_id}")
    return tickets[:limit]
