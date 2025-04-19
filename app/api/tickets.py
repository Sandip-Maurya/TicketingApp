# app/api/tickets.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database_setup.database import get_db
from app.services.event_helpers import get_unsold_ticket_status, get_event_ticket_types

router = APIRouter()

@router.get('/show-ticket-status')
def show_unsold_ticket_status(db: Session = Depends(get_db)):
    return get_unsold_ticket_status(db)

@router.get('/ticket-types')
def show_event_ticket_types(db: Session = Depends(get_db)):
    return get_event_ticket_types(db)
