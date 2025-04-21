# app/services/order_utils.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from datetime import datetime
from app.database_setup.model import Event, Ticket, Order, OrderStatus
from app.services.discount_strategy import get_best_discount
from app.schemas.order_schemas import OrderPayload


def validate_event(event_id: int, db: Session) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} does not exist")
    return event


def get_available_tickets(event_id: int, db: Session) -> list[Ticket]:
    return db.query(Ticket).filter(
        Ticket.event_id == event_id,
        Ticket.is_sold == False
    ).all()


def apply_discount(db: Session, event_id: int, ticket_type: str, qty: int, total: float):
    discount = get_best_discount(db, event_id, ticket_type, qty)
    if discount:
        discount_amount = (discount.percentage_off / 100) * total
        return discount, total - discount_amount
    return None, total

def create_order_record(
    payload: OrderPayload,
    selected_ticket_ids: List[int],
    total_price: float,
    price_after_discount: float,
    discount_ids: List[int],
    db: Session
) -> Order:
    # 1️⃣ Build the Order object
    order = Order(
        event_id=payload.event_id,
        sold_tickets_ids=selected_ticket_ids,
        quantity_sold=len(selected_ticket_ids),
        total_tickets_price=total_price,
        price_after_discount=price_after_discount,
        status=OrderStatus.reserved,
        user_name=payload.user_name,
        user_email=payload.user_email,
        applied_discount_id=discount_ids[0] if discount_ids else None
    )

    # 2️⃣ Add and flush so `order.id` is populated (no commit here)
    db.add(order)
    db.flush()

    # 3️⃣ Mark each selected ticket as sold
    tickets = (
        db.query(Ticket)
          .filter(Ticket.id.in_(selected_ticket_ids))
          .all()
    )
    for ticket in tickets:
        ticket.is_sold = True
        db.add(ticket)
    db.flush()

    # 4️⃣ Refresh the order to populate relationships, still inside the transaction
    db.refresh(order)

    return order


def reserve_tickets_by_type(
    db: Session,
    event_id: int,
    ticket_counts: dict[str, int],
    user_email: str
) -> list[Ticket]:
    # 1️⃣ Check event validity and timing
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='Event not found.'
        )
    
    if event.event_datetime < datetime.now():
        print("DEBUG: Event expired check triggered")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='Cannot reserve tickets for an event that has already started or finished.'
        )

    # 2️⃣ Fetch unsold & unreserved tickets
    tickets = (
        db.query(Ticket)
          .filter(
              Ticket.event_id == event_id,
              Ticket.is_sold == False,
              Ticket.is_reserved == False,
              Ticket.ticket_type.in_(ticket_counts.keys())
          )
          .order_by(Ticket.id.asc())
          .all()
    )

    # 3️⃣ Check if all requested types are available
    shortage = []
    type_to_available = {
        typ: [t for t in tickets if t.ticket_type.value == typ]
        for typ in ticket_counts
    }

    for typ, count in ticket_counts.items():
        available = type_to_available.get(typ, [])
        if len(available) < count:
            shortage.append(f"{count - len(available)} '{typ}'")

    if shortage:
        print("DEBUG: Ticket shortage triggered")

        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Not enough tickets available: {', '.join(shortage)} ticket(s) missing."
        )

    # 4️⃣ All good – mark tickets as reserved
    reserved = []
    for typ, count in ticket_counts.items():
        for t in type_to_available[typ][:count]:
            t.is_reserved = True
            t.issued_to = user_email
            db.add(t)
            reserved.append(t)

    db.flush()
    return reserved
