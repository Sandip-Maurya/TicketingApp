# app/admin/tickets_management.py

from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database_setup.database import get_db
from app.database_setup.model import Event, TicketTypes
from app.schemas.ticket_schemas import (
    TicketCreate,
    TicketsAddResponse,
    TicketSummary,
    TicketDelete,
    TicketsDeleteResponse
)
from app.admin.services.tickets_service import create_tickets, delete_unsold_tickets

router = APIRouter()

# Add fresh tickets to an event
@router.post(
    '',
    response_model = TicketsAddResponse,
    status_code = status.HTTP_201_CREATED,
    summary = 'Add fresh tickets to an event'
)
def add_more_tickets(
    event_id: int,
    items: List[TicketCreate],
    db: Session = Depends(get_db)
):
    # Validate event existence
    if not db.query(Event).filter(Event.id == event_id).first():
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f'Event {event_id} not found'
        )

    tickets = create_tickets(db, event_id, items)

    # Build summaries by ticket type
    summary: Dict[str, TicketSummary] = {}
    for tt in TicketTypes:
        group = [t for t in tickets if t.ticket_type == tt]
        if group:
            summary[tt.value] = TicketSummary(
                price = group[0].price,
                count = len(group)
            )

    return {
        'message': 'Tickets added successfully',
        'event_id': event_id,
        'regular': summary.get('regular'),
        'vip': summary.get('vip')
    }

# Delete unsold tickets from an event
@router.delete(
    '/delete',
    response_model = TicketsDeleteResponse,
    status_code = status.HTTP_200_OK,
    summary = 'Delete unsold tickets'
)
def delete_more_tickets(
    event_id: int,
    items: List[TicketDelete],
    db: Session = Depends(get_db)
):
    # Validate event existence
    if not db.query(Event).filter(Event.id == event_id).first():
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = f'Event {event_id} not found'
        )

    deleted_map = delete_unsold_tickets(db, event_id, items)

    # Build summary and detect excessive delete requests
    overs = False
    summary = {}
    for item in items:
        removed = deleted_map.get(item.ticket_type.value, [])
        if removed:
            summary[item.ticket_type.value] = TicketSummary(
                price = removed[0].price,
                count = len(removed)
            )
        if item.count > len(removed):
            overs = True

    total_removed = sum(len(v) for v in deleted_map.values())
    if total_removed == 0:
        msg = 'No unsold tickets available to delete.'
    elif overs:
        msg = 'Requested delete counts exceeded available tickets; deleted as many as possible.'
    else:
        msg = 'Tickets deleted successfully.'

    return {
        'message': msg,
        'event_id': event_id,
        'regular': summary.get('regular'),
        'vip': summary.get('vip')
    }
