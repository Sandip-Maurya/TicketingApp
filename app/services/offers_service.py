# # app/services/offers_service.py

# from collections import defaultdict
# from fastapi import HTTPException
# from sqlalchemy.orm import Session

# from app.database_setup.model import Ticket
# from app.schemas.order_schemas import CheckOfferRequest, OfferInfo
# from app.services.discount_strategy import get_best_discount_strategy, get_best_discount
# from app.services.order_utils import validate_event


# def preview_offers(payload: CheckOfferRequest, db: Session) -> dict:
#     # Step 0: Validate event
#     validate_event(payload.event_id, db)

#     # Step 1: Pull requested tickets & ensure availability
#     selected_tickets = []
#     for ticket_type, qty in payload.tickets.model_dump().items():
#         if qty <= 0:
#             continue
#         batch = (
#             db.query(Ticket)
#             .filter(
#                 Ticket.event_id == payload.event_id,
#                 Ticket.ticket_type == ticket_type,
#                 Ticket.is_sold == False,
#             )
#             .limit(qty)
#             .all()
#         )
#         if len(batch) < qty:
#             return {
#                 'message': f'Only {len(batch)} {ticket_type.value} tickets available',
#                 'tickets_available': False
#             }
#         selected_tickets.extend(batch)

#     if not selected_tickets:
#         raise HTTPException(status_code=400, detail='No valid tickets requested.')

#     total_price = sum(t.price for t in selected_tickets)

#     # Step 2: Compute best‐discount Strategy
#     discounts_applied, price_after_discount, strategy = get_best_discount_strategy(
#         db, payload.event_id, selected_tickets
#     )

#     # Step 3: Build ticket_prices map
#     grouped = defaultdict(list)
#     for t in selected_tickets:
#         grouped[t.ticket_type.value].append(t)
#     ticket_prices = {tt: grp[0].price for tt, grp in grouped.items()}

#     # Step 4: Gather every applicable discount
#     all_applicable_discounts = []
    
#     seen = set()

#     # a) Per‐type discounts
#     for tt, grp in grouped.items():
#         qty = len(grp)
#         disc = get_best_discount(db, payload.event_id, tt, qty)
#         if disc and disc.id not in seen:
#             seen.add(disc.id)
#             group_total = sum(t.price for t in grp)
#             saving = group_total * disc.percentage_off / 100
#             all_applicable_discounts.append(OfferInfo(
#                 name=disc.name,
#                 percentage_off=disc.percentage_off,
#                 saving=round(saving, 2),
#                 price=grp[0].price,
#                 min_tickets=disc.min_tickets,
#                 applicable_ticket_type=tt,
#             ))

#     # b) Combined discount
#     combo = get_best_discount(db, payload.event_id, 'both', len(selected_tickets))
#     if combo and combo.id not in seen:
#         saving = total_price * combo.percentage_off / 100
#         # for combined, price per‐ticket isn't meaningful, set to 0 or omit
#         all_applicable_discounts.append(OfferInfo(
#             name=combo.name,
#             percentage_off=combo.percentage_off,
#             saving=round(saving, 2),
#             price=0.0,
#             min_tickets=combo.min_tickets,
#             applicable_ticket_type='both',
#         ))

#     # Step 5: Build the applied_discounts list
#     applied_discounts = []
#     for disc in discounts_applied:
#         if strategy == 'combined':
#             tt = 'both'
#             grp_total = total_price
#             grp_after = price_after_discount
#         else:
#             tt = disc.applicable_ticket_types.value
#             grp_total = sum(t.price for t in grouped[tt])
#             grp_after = round(grp_total * (1 - disc.percentage_off / 100), 2)

#         applied_discounts.append({
#             'ticket_type': tt,
#             'name': disc.name,
#             'percentage_off': disc.percentage_off,
#             'min_tickets': disc.min_tickets,
#             'saving': round(grp_total * disc.percentage_off / 100, 2),
#             'total_price': grp_total,
#             'price_after_discount': grp_after,
#         })

#     return {
#         'message': 'Here is the best offer for you.' if applied_discounts else
#                    'No active offers; buy more tickets to unlock savings!',
#         'your_input': {
#             'event_id': payload.event_id,
#             'tickets': {k: v for k, v in payload.tickets.model_dump().items()}
#         },
#         'ticket_prices': ticket_prices,
#         'applicable_discounts': all_applicable_discounts,
#         'applied_discounts': applied_discounts,
#         'total_price': total_price,
#         'price_after_discount': price_after_discount,
#         'tickets_available': True
#     }

''''''

# from typing import Dict
# from datetime import datetime

# from fastapi import HTTPException
# from sqlalchemy.orm import Session

# from app.database_setup.model import Event, Ticket, Discount, DiscountApplicability
# from app.schemas.offer_schemas import (
#     CheckOfferRequest, OffersResponse,
#     CategoryOffer, Offer, OfferTotal
# )

# def check_offers(db: Session, payload: CheckOfferRequest) -> OffersResponse:
#     # 1. Validate event
#     event = db.query(Event).filter(Event.id == payload.event_id).first()
#     if not event:
#         raise HTTPException(status_code=404, detail='Event not found')

#     tickets_out: Dict[str, CategoryOffer] = {}
#     total_before = 0.0
#     total_savings = 0.0

#     for ttype, qty in payload.tickets.model_dump().items():
#         # 2. Fetch unit price
#         ticket = db.query(Ticket).filter(
#             Ticket.event_id == payload.event_id,
#             Ticket.ticket_type == ttype
#         ).first()
#         if not ticket:
#             raise HTTPException(status_code=404, detail=f'No {ttype} tickets for event')
#         unit_price = ticket.price
#         subtotal = unit_price * qty

#         # 3. Gather all applicable discounts
#         raw_discounts = db.query(Discount).filter(
#             Discount.valid_till >= datetime.now(),
#             Discount.min_tickets <= qty
#         ).all()
#         eligible: list[Offer] = []
#         for d in raw_discounts:
#             if d.applicable_ticket_types.value == ttype or d.applicable_ticket_types == DiscountApplicability.both:
#                 saving = d.percentage_off / 100 * subtotal
#                 per_ticket = saving / qty
#                 final_per_ticket = unit_price - per_ticket
#                 eligible.append(Offer(
#                     name=d.name,
#                     percentage_off=d.percentage_off,
#                     saving=saving,
#                     discount_per_ticket=per_ticket,
#                     final_price_per_ticket=final_per_ticket
#                 ))

#         # 4. Choose the best
#         if eligible:
#             selected = max(eligible, key=lambda o: o.saving)
#             saving_total = selected.saving
#         else:
#             selected = Offer(
#                 name='',
#                 percentage_off=0.0,
#                 saving=0.0,
#                 discount_per_ticket=0.0,
#                 final_price_per_ticket=unit_price
#             )
#             saving_total = 0.0

#         # 5. Record and accumulate
#         tickets_out[ttype] = CategoryOffer(
#             count=qty,
#             unit_price=unit_price,
#             eligible_offers=eligible,
#             selected_offer=selected
#         )
#         total_before += subtotal
#         total_savings += saving_total

#     total_after = total_before - total_savings
#     summary = OfferTotal(before=total_before, savings=total_savings, after=total_after)

#     return OffersResponse(
#         message='Here are the offers available for your selection.',
#         tickets=tickets_out,
#         total=summary
#     )

''''''

from typing import Dict, Optional
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database_setup.model import Event, Ticket, Discount, DiscountApplicability
from app.schemas.offer_schemas import (
    CheckOfferRequest, OffersResponse,
    CategoryOffer, Offer, OfferTotal
)

def check_offers(db: Session, payload: CheckOfferRequest) -> OffersResponse:
    # 1. Validate event exists
    event = db.query(Event).filter(Event.id == payload.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    tickets_out: Dict[str, CategoryOffer] = {}
    total_before = 0.0
    total_savings = 0.0

    # 2. Process each ticket type
    for ttype, qty in payload.tickets.model_dump().items():
        ticket = db.query(Ticket).filter(
            Ticket.event_id == payload.event_id,
            Ticket.ticket_type == ttype
        ).first()
        if not ticket:
            raise HTTPException(status_code=404, detail=f'No {ttype} tickets for event')

        unit_price = ticket.price
        subtotal = unit_price * qty

        # find eligible discounts for this type
        raw = db.query(Discount).filter(
            Discount.valid_till >= datetime.now(),
            Discount.min_tickets <= qty
        ).all()
        eligible: list[Offer] = []
        for d in raw:
            if (d.applicable_ticket_types.value == ttype
                    or d.applicable_ticket_types == DiscountApplicability.both):
                saving = d.percentage_off / 100 * subtotal
                per_ticket = saving / qty
                final_per_ticket = unit_price - per_ticket
                eligible.append(Offer(
                    name=d.name,
                    percentage_off=d.percentage_off,
                    saving=saving,
                    discount_per_ticket=per_ticket,
                    final_price_per_ticket=final_per_ticket
                ))

        if eligible:
            selected = max(eligible, key=lambda o: o.saving)
            saving_total = selected.saving
        else:
            selected = Offer(
                name='',
                percentage_off=0.0,
                saving=0.0,
                discount_per_ticket=0.0,
                final_price_per_ticket=unit_price
            )
            saving_total = 0.0

        tickets_out[ttype] = CategoryOffer(
            count=qty,
            unit_price=unit_price,
            eligible_offers=eligible,
            selected_offer=selected
        )
        total_before += subtotal
        total_savings += saving_total

    # 3. Process combined‑ticket offers
    combined_count = sum(payload.tickets.model_dump().values())
    combined_subtotal = total_before

    raw_combined = db.query(Discount).filter(
        Discount.valid_till >= datetime.now(),
        Discount.min_tickets <= combined_count,
        Discount.applicable_ticket_types == DiscountApplicability.both
    ).all()
    eligible_combined: list[Offer] = []
    for d in raw_combined:
        saving = d.percentage_off / 100 * combined_subtotal
        per_ticket = round(saving / combined_count, 2)
        eligible_combined.append(Offer(
            name=d.name,
            percentage_off=d.percentage_off,
            saving=saving,
            discount_per_ticket=per_ticket,
            final_price_per_ticket=None
        ))

    if eligible_combined:
        selected_combined = max(eligible_combined, key=lambda o: o.saving)
        combined_saving = selected_combined.saving
    else:
        selected_combined = Offer(
            name='',
            percentage_off=0.0,
            saving=0.0,
            discount_per_ticket=0.0,
            final_price_per_ticket=None
        )
        combined_saving = 0.0

    tickets_out['combined'] = CategoryOffer(
        count=combined_count,
        unit_price=None,
        eligible_offers=eligible_combined,
        selected_offer=selected_combined
    )
    total_savings += combined_saving

    # 4. Build summary
    total_after = total_before - total_savings
    summary = OfferTotal(before=total_before, savings=total_savings, after=total_after)

    return OffersResponse(
        message='Here are the offers available for your selection.',
        tickets=tickets_out,
        total=summary
    )
