# app/admin/services

from typing import List, Dict
from sqlalchemy.orm import Session
from app.database_setup.model import Ticket
from app.schemas.ticket_schemas import TicketCreate, TicketDelete

def create_tickets(db: Session, event_id: int, items: List[TicketCreate]) -> List[Ticket]:
    new_tickets = [
        Ticket(
            event_id = event_id,
            ticket_type = item.ticket_type,
            price = item.price,
            is_sold = False
        )
        for item in items
        for _ in range(item.quantity)
    ]

    db.add_all(new_tickets)
    db.commit()

    for t in new_tickets:
        db.refresh(t)

    return new_tickets

def delete_unsold_tickets(
    db: Session,
    event_id: int,
    items: List[TicketDelete]
) -> Dict[str, List[Ticket]]:
    
    deleted_map: Dict[str, List[Ticket]] = {}

    for item in items:
        to_delete = (
            db.query(Ticket)
              .filter(
                  Ticket.event_id == event_id,
                  Ticket.is_sold == False,
                  Ticket.ticket_type == item.ticket_type
              )
              .order_by(Ticket.id.desc())
              .limit(item.count)
              .all()
        )

        for t in to_delete:
            db.delete(t)

        deleted_map[item.ticket_type.value] = to_delete

    db.commit()
    return deleted_map
