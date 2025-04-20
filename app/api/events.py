# app/api/events.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database_setup.database import get_db
from app.database_setup.model import Event
from app.schemas.event_schemas import EventOut
from typing import List

router = APIRouter()

@router.get(
        '/get-all-events', 
        response_model = List[EventOut], 
        summary = 'Get details of all the events')

def get_all_events(
    db: Session = Depends(get_db)
) -> List[EventOut]:
    return db.query(Event).all()
