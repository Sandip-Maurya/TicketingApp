from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.database_setup.model import Order, Ticket, OrderStatus
from app.schemas.order_schemas import OrderResponse, TicketInfo
from app.services.discount_strategy import get_best_discount_strategy

def build_ticket_info(
    tickets: List[Ticket],
    discounts_used: List,
    strategy: str
) -> Dict[str, TicketInfo]:
    """
    Group tickets by type and assemble per‐type TicketInfo,
    applying either 'separate' or 'combined' discount strategy.
    """
    grouped: Dict[str, List[Ticket]] = {'regular': [], 'vip': []}
    for t in tickets:
        grouped[t.ticket_type.value].append(t)

    info: Dict[str, TicketInfo] = {}
    for typ, group in grouped.items():
        ids = [t.id for t in group]
        unit_price = group[0].price if group else 0.0

        # pick the right discount object
        if strategy == 'separate':
            disc = next(
                (d for d in discounts_used
                 if d.applicable_ticket_types.value == typ),
                None
            )
        else:  # 'combined'
            disc = next(
                (d for d in discounts_used
                 if d.applicable_ticket_types.value == 'both'),
                None
            )

        offer_name = disc.name if disc else None
        discount_per_ticket = (
            (disc.percentage_off / 100.0) * unit_price
            if disc else 0.0
        )
        final_unit = unit_price - discount_per_ticket

        info[typ] = TicketInfo(
            ticket_ids=ids,
            count=len(ids),
            unit_price=unit_price,
            offer=offer_name,
            discount_per_ticket=discount_per_ticket,
            final_price_per_ticket=final_unit
        )
    return info

def build_order_response(
    db: Session,
    order: Order,
    tickets: List[Ticket],
    message: str
) -> OrderResponse:
    """
    Given an Order and its tickets, re‐runs discount logic,
    flips totals, and builds the final Pydantic response.
    """
    # 1️⃣ Recompute discounts
    discounts_used, discounted_price, strategy = get_best_discount_strategy(
        db, order.event_id, tickets
    )
    total_price = sum(t.price for t in tickets)

    # 2️⃣ Build per‐type ticket sections
    ticket_info = build_ticket_info(tickets, discounts_used, strategy)

    # 3️⃣ Return the unified response
    return OrderResponse(
        message=message,
        order_id=order.id,
        user={"name": order.user_name, "email": order.user_email},
        tickets=ticket_info,
        total_price=total_price,
        discounted_price=discounted_price
    )
