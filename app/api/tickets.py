# app/api/tickets.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database_setup.database import get_db
from app.services.ticket_service import get_unsold_ticket_status, get_ticket_types
from app.schemas.ticket_schemas import EventTicketTypes, EventUnsoldTickets

router = APIRouter()

@router.get(
    '/show-ticket-status',
    response_model = List[EventUnsoldTickets],
    summary = 'Show unsold ticket count and price for each event',
)
def show_unsold_ticket_status(db: Session = Depends(get_db)):
    raw = get_unsold_ticket_status(db)
    return [
        EventUnsoldTickets(
            event_name = event,
            regular = data['regular'],
            vip = data['vip'],
        )
        for event, data in raw.items()
    ]

@router.get(
    '/ticket-types',
    response_model = List[EventTicketTypes],
    summary = 'List available ticket types for each event',
)
def show_event_ticket_types(db: Session = Depends(get_db)):
    ticket_types = get_ticket_types(db)
    return ticket_types
