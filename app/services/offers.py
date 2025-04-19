from collections import defaultdict
from typing import Optional

from sqlalchemy.orm import Session
from app.database_setup.model import Ticket, Discount
from app.schemas.order_schemas import OfferPreviewRequest, OfferPreviewResponse, OfferInfo
from app.services.discounts import get_best_discount


def preview_offers(payload: OfferPreviewRequest, db: Session) -> OfferPreviewResponse:
    event_id = payload.event_id
    ticket_requests = payload.tickets

    # 1. Fetch unsold tickets for the event
    available_tickets = db.query(Ticket).filter(
        Ticket.event_id == event_id,
        Ticket.is_sold == False
    ).all()

    # Group available tickets by type
    available_by_type = defaultdict(list)
    for ticket in available_tickets:
        available_by_type[ticket.ticket_type.value].append(ticket)

    # Check availability
    tickets_available = all(
        len(available_by_type.get(ticket_type.value, [])) >= qty
        for ticket_type, qty in ticket_requests.items()
    )

    if not tickets_available:
        return OfferPreviewResponse(
            message='Not enough tickets available.',
            your_input=payload.dict(),
            applicable_discounts=[],
            applied_discounts=None,
            total_price=0,
            price_after_discount=0,
            tickets_available=False
        )

    # Select required tickets
    selected_tickets = []
    for ticket_type, qty in ticket_requests.items():
        selected_tickets.extend(available_by_type[ticket_type.value][:qty])

    total_price = sum(t.price for t in selected_tickets)

    # Strategy A: Separate Discounts
    separate_price = 0
    separate_discounts = []
    separate_savings = []

    grouped = defaultdict(list)
    for ticket in selected_tickets:
        grouped[ticket.ticket_type.value].append(ticket)

    for ticket_type, group in grouped.items():
        type_total = sum(t.price for t in group)
        discount = get_best_discount(db, event_id, ticket_type, len(group))
        if discount:
            saving = (discount.percentage_off / 100) * type_total
            separate_price += type_total - saving
            separate_discounts.append(OfferInfo(
                name=discount.name,
                percentage_off=discount.percentage_off,
                saving=round(saving, 2)
            ))
            separate_savings.append(saving)
        else:
            separate_price += type_total

    # Strategy B: Combined Discount
    combined_discount = get_best_discount(db, event_id, 'both', len(selected_tickets))
    if combined_discount:
        combo_saving = (combined_discount.percentage_off / 100) * total_price
        combo_price = total_price - combo_saving
        combo_offer_info = OfferInfo(
            name=combined_discount.name,
            percentage_off=combined_discount.percentage_off,
            saving=round(combo_saving, 2)
        )
    else:
        combo_price = total_price
        combo_saving = 0
        combo_offer_info = None

    # Pick best strategy
    if combo_price < separate_price:
        applied = combo_offer_info
        strategy = 'combined'
        final_price = combo_price
        applicable = [combo_offer_info] if combo_offer_info else []
    elif separate_savings:
        applied = max(separate_discounts, key=lambda x: x.saving)
        strategy = 'separate'
        final_price = separate_price
        applicable = separate_discounts
    else:
        # No discounts apply
        return OfferPreviewResponse(
            message='No discounts apply. Add more tickets to unlock offers!',
            your_input=payload.dict(),
            applicable_discounts=[],
            applied_discounts=None,
            total_price=round(total_price, 2),
            price_after_discount=round(total_price, 2),
            tickets_available=True
        )

    return OfferPreviewResponse(
        message='Offers preview generated successfully.',
        your_input=payload.dict(),
        applicable_discounts=applicable,
        applied_discounts=applied.name if applied else None,
        total_price=round(total_price, 2),
        price_after_discount=round(final_price, 2),
        tickets_available=True
    )
