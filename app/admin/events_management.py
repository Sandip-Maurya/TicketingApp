# app/admin/events_management.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database_setup.database import get_db
from app.schemas.event_schemas import EventCreate, EventUpdate, EventResponse, EventDeleteResponse
from app.admin.services.events_service import (
    create_event,
    update_event as svc_update_event,
    delete_event as svc_delete_event
)

router = APIRouter()

@router.post(
    '/',
    response_model = EventResponse,
    status_code = status.HTTP_201_CREATED,
    summary = 'Add more events'
)
def add_event(
    payload: EventCreate,
    db: Session = Depends(get_db)
):
    new_event = create_event(db, payload)
    return {
        "message": "Event created successfully",
        "event": new_event
    }

@router.put(
    '/{event_id}',
    response_model = EventResponse,
    status_code = status.HTTP_200_OK,
    summary = 'Update an event by its ID'
)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db)
):
    updated = svc_update_event(db, event_id, payload)
    if not updated:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f'Event with {event_id = } not found'
        )
    return {
        "message": "Event updated successfully",
        "event": updated
    }


@router.delete(
    '/{event_id}',
    response_model = EventDeleteResponse,
    status_code = status.HTTP_200_OK,
    summary = 'Delete an event by its ID'
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = svc_delete_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f'Event with {event_id = } not found'
        )

    return {
        "message": "Event deleted successfully",
        "id": event.id,
        "name": event.name
    }
