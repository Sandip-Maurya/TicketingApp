from typing import List, Dict
from sqlalchemy.orm import Session
from app.database_setup.model import Ticket
from app.schemas.ticket_schemas import TicketCreate, TicketDelete

def create_tickets(db: Session, event_id: int, items: List[TicketCreate]) -> List[Ticket]:
    # Build all Ticket objects in memory
    new_tickets = []
    for item in items:
        new_tickets += [
            Ticket(
                event_id=event_id,
                ticket_type=item.ticket_type,
                price=item.price,
                is_sold=False
            )
            for _ in range(item.quantity)
        ]

    # Bulk‐save them in one go
    db.add_all(new_tickets)
    db.commit()

    # If you need the generated IDs, you can still refresh in bulk:
    for t in new_tickets:
        db.refresh(t)

    return new_tickets


def delete_unsold_tickets(
    db: Session,
    event_id: int,
    items: List[TicketDelete]
) -> Dict[str, List[Ticket]]:
    """
    Deletes up to `item.count` unsold tickets of each type,
    ordered by descending ID (so higher IDs go first).
    Returns a dict mapping ticket_type.value -> list of deleted Ticket objects.
    """
    deleted_map: Dict[str, List[Ticket]] = {}

    for item in items:
        q = (
            db.query(Ticket)
              .filter(
                  Ticket.event_id == event_id,
                  Ticket.is_sold == False,
                  Ticket.ticket_type == item.ticket_type
              )
              .order_by(Ticket.id.desc())
              .limit(item.count)
        )
        to_delete = q.all()
        for t in to_delete:
            db.delete(t)
        # record what was actually deleted
        deleted_map[item.ticket_type.value] = to_delete

    db.commit()
    return deleted_map

