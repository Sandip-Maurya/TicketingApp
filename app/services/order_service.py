# app/services/order_service.py

from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.schemas.order_schemas import (
    OrderCreate, OrderResponse,
    TicketCategoryDetail, TicketsOut, OrderTotal, UserOut
)
from app.services.order_utils import validate_event, reserve_tickets_by_type, create_order_record
from app.services.discount_strategy import get_best_discount_strategy
from app.database_setup.model import Ticket

def place_order(db: Session, payload: OrderCreate) -> OrderResponse:
    # 1. Validate event
    validate_event(payload.event_id, db)

    # 2. Reserve tickets
    reserved: List[Ticket] = reserve_tickets_by_type(
        db,
        payload.event_id,
        payload.tickets.model_dump(),
        payload.user_email
    )
    if not reserved:
        # Handled already in util
        raise HTTPException(status_code=422, detail='Please select at least one ticket.')

    # 3. Determine best discounts
    discounts_used, final_total, strategy = get_best_discount_strategy(
        db, payload.event_id, reserved
    )
    total_before = sum(t.price for t in reserved)
    total_savings = total_before - final_total

    # 4. Group tickets by type
    grouped: Dict[str, List[Ticket]] = {'regular': [], 'vip': []}
    for t in reserved:
        grouped[t.ticket_type.value].append(t)

    # 5. Build TicketsOut with per‑category offers
    tickets_out = TicketsOut(
        **{
            typ: TicketCategoryDetail(
                ticket_ids=[t.id for t in group],
                count=len(group),
                unit_price=group[0].price if group else 0.0,
                # pick the matching discount name if separate strategy
                offer=(
                    next(
                        (d.name for d in discounts_used
                         if d.applicable_ticket_types.value == typ),
                        None
                    )
                    if strategy == 'separate' else None
                ),
                # per-ticket discount for this category
                discount_per_ticket=(
                    (next(
                        (d.percentage_off for d in discounts_used
                         if d.applicable_ticket_types.value == typ),
                        0.0
                     ) / 100) * (group[0].price if group else 0.0)
                    if strategy == 'separate' and group else 0.0
                ),
                # final per-ticket price
                final_price_per_ticket=(
                    (group[0].price if group else 0.0)
                    - (
                        (next(
                            (d.percentage_off for d in discounts_used
                             if d.applicable_ticket_types.value == typ),
                            0.0
                        ) / 100) * (group[0].price if group else 0.0)
                    )
                    if strategy == 'separate' and group else (group[0].price if group else 0.0)
                )
            )
            for typ, group in grouped.items()
        }
    )

    # 6. Persist order
    order = create_order_record(
        payload,
        [t.id for t in reserved],
        total_before,
        final_total,
        [d.id for d in discounts_used],
        db
    )

    # 7. Return response
    return OrderResponse(
        message='Your order was successful.',
        order_id=order.id,
        user=UserOut(name=payload.user_name, email=payload.user_email),
        tickets=tickets_out,
        total=OrderTotal(
            before_discount=total_before,
            savings=total_savings,
            after_discount=final_total
        ),
        applied_offers=[d.name for d in discounts_used]
    )
