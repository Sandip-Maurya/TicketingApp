# app/services/order_utils.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
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
# app/services/ticket_utils.py

def reserve_tickets_by_type(
    db: Session,
    event_id: int,
    ticket_counts: dict[str,int],
    user_email: str
) -> list[Ticket]:
    # 1️⃣ Query unsold & unreserved tickets
    tickets = (
        db.query(Ticket)
          .filter(
              Ticket.event_id == event_id,
              Ticket.is_sold   == False,
              Ticket.is_reserved == False,
              Ticket.ticket_type.in_(ticket_counts.keys())
          )
          .order_by(Ticket.id.asc())
          .all()
    )

    reserved = []
    # 2️⃣ Reserve as many as requested per type
    for typ, count in ticket_counts.items():
        to_take = [t for t in tickets if t.ticket_type.value == typ][:count]
        for t in to_take:
            t.is_reserved = True
            t.issued_to = user_email     
            db.add(t)
            reserved.append(t)

    db.flush()
    return reserved
