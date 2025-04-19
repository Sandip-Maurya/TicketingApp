# app/service/order_helpers.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from app.database_setup.model import Event, Ticket, Order
from app.services.discounts import get_best_discount
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
    order = Order(
        event_id=payload.event_id,
        sold_tickets_ids=selected_ticket_ids,
        quantity_sold=len(selected_ticket_ids),
        total_tickets_price=total_price,
        price_after_discount=price_after_discount,
        status='confirmed',
        user_name=payload.user_name,
        user_email=payload.user_email,
        applied_discount_id=discount_ids[0] if discount_ids else None  # storing only one for now
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

from fastapi import HTTPException

def reserve_tickets_by_type(
    db: Session,
    event_id: int,
    ticket_requests: dict,
    user_email: str
) -> list[Ticket]:
    all_selected_tickets = []

    for ticket_type_str, qty in ticket_requests.items():
        if qty <= 0:
            continue

        tickets = db.query(Ticket).filter(
            Ticket.event_id == event_id,
            Ticket.ticket_type == ticket_type_str,
            Ticket.is_sold == False
        ).limit(qty).all()

        if len(tickets) < qty:
            raise HTTPException(
                status_code=422,
                detail=f'Only {len(tickets)} {ticket_type_str.value} tickets available'
            )

        for ticket in tickets:
            ticket.is_sold = True
            ticket.issued_to = user_email
            db.add(ticket)

        all_selected_tickets.extend(tickets)

    return all_selected_tickets
