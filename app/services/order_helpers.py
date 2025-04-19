from sqlalchemy.orm import Session
from fastapi import HTTPException
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


def select_and_reserve_tickets(tickets: list[Ticket], quantity: int, email: str, db: Session) -> tuple[list, list]:
    selected = tickets[:quantity]
    ids = []
    for ticket in selected:
        ticket.is_sold = True
        ticket.issued_to = email
        db.add(ticket)
        ids.append(ticket.id)
    return selected, ids


def apply_discount(db: Session, event_id: int, ticket_type: str, qty: int, total: float):
    discount = get_best_discount(db, event_id, ticket_type, qty)
    if discount:
        discount_amount = (discount.percentage_off / 100) * total
        return discount, total - discount_amount
    return None, total


def create_order_record(payload: OrderPayload, selected_ticket_ids: list, total_price: float,
                        price_after_discount: float, discount, db: Session) -> Order:
    order = Order(
        event_id=payload.event_id,
        sold_tickets_ids=selected_ticket_ids,
        quantity_sold=payload.quantity,
        total_tickets_price=total_price,
        price_after_discount=price_after_discount,
        status='confirmed',
        user_name=payload.user_name,
        user_email=payload.user_email,
        applied_discount_id=discount.id if discount else None
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
