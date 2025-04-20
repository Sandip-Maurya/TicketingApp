# # app/services/order_service.py

# from collections import defaultdict
# from sqlalchemy.orm import Session
# from fastapi import HTTPException
# from app.schemas.order_schemas import OrderPayload
# from app.services.order_utils import validate_event, reserve_tickets_by_type, create_order_record
# from app.services.discount_strategy import get_best_discount_strategy

# def process_order(payload: OrderPayload, db: Session) -> dict:

#     total_requested = sum(payload.tickets.values())
#     if total_requested <= 0:
#         raise HTTPException(
#             status_code=422,
#             detail='You must request at least one ticket of any type.'
#         )


#     # 1. Validate event
#     validate_event(payload.event_id, db)

#     # 2. Reserve tickets (raises error if not enough)
#     selected_tickets = reserve_tickets_by_type(
#         db,
#         payload.event_id,
#         payload.tickets,
#         payload.user_email
#     )

#     ticket_ids = [t.id for t in selected_tickets]
#     total_price = sum(t.price for t in selected_tickets)

#     # 3. Get best discount strategy
#     discounts_applied, price_after_discount, strategy = get_best_discount_strategy(
#         db,
#         payload.event_id,
#         selected_tickets
#     )

#     # 4. Save order
#     order = create_order_record(
#         payload=payload,
#         selected_ticket_ids=ticket_ids,
#         total_price=total_price,
#         price_after_discount=price_after_discount,
#         discount_ids=[d.id for d in discounts_applied],
#         db=db
#     )

#     # 5. Compute saved_amount per discount
#     #    First, group ticket‑prices by ticket_type
#     group_totals = defaultdict(float)
#     for t in selected_tickets:
#         group_totals[t.ticket_type.value] += t.price

#     response_discounts = []
#     if strategy == 'combined':
#         # combined discount applies to the whole basket
#         for d in discounts_applied:
#             saved = total_price * d.percentage_off / 100
#             response_discounts.append({
#                 'name': d.name,
#                 'applicable_ticket_types': d.applicable_ticket_types.value,
#                 'percentage_off': d.percentage_off,
#                 'saved_amount': round(saved, 2),
#             })
#     else:
#         # separate discounts apply per ticket type
#         for d in discounts_applied:
#             ttype = d.applicable_ticket_types.value
#             saved = group_totals.get(ttype, 0.0) * d.percentage_off / 100
#             response_discounts.append({
#                 'name': d.name,
#                 'applicable_ticket_types': ttype,
#                 'percentage_off': d.percentage_off,
#                 'saved_amount': round(saved, 2),
#             })

#     return {
#         'message': 'Your order is successfully.',
#         'order_id': order.id,
#         'ticket_ids': ticket_ids,
#         'total_price': total_price,
#         'price_after_discount': price_after_discount,
#         'savings': round(total_price - price_after_discount, 2),
#         'discount_applied': response_discounts
#     }

''''''

# from typing import Dict, List
# from sqlalchemy.orm import Session
# from fastapi import HTTPException

# from app.schemas.order_schemas import (
#     OrderCreate, OrderResponse,
#     TicketCategoryDetail, TicketsOut, OrderTotal, UserOut
# )
# from app.services.order_utils import (
#     validate_event,
#     reserve_tickets_by_type,
#     apply_discount,
#     create_order_record
# )

# def place_order(db: Session, payload: OrderCreate) -> OrderResponse:
#     # 1. Ensure event exists
#     validate_event(payload.event_id, db)

#     # 2. Reserve (mark sold) and fetch ticket objects
#     tickets = reserve_tickets_by_type(
#         db,
#         payload.event_id,
#         payload.tickets.model_dump(),
#         payload.user_email
#     )
#     if not tickets:
#         # raise ValueError('No tickets selected')
#         raise HTTPException(
#             status_code=422,
#             detail='You must request at least one ticket of any type.'
#         )


#     # 3. Group by type
#     grouped: Dict[str, List] = {'regular': [], 'vip': []}
#     for t in tickets:
#         grouped[t.ticket_type.value].append(t)

#     # 4. Build per-category details
#     tickets_out = {}
#     total_before = 0.0
#     total_savings = 0.0

#     for typ in ('regular', 'vip'):
#         group = grouped[typ]
#         count = len(group)
#         if count:
#             ids = [t.id for t in group]
#             unit_price = group[0].price
#             subtotal = unit_price * count

#             discount_obj, after_total = apply_discount(
#                 db, payload.event_id, typ, count, subtotal
#             )
#             if discount_obj:
#                 offer = discount_obj.name
#                 per_ticket_discount = (discount_obj.percentage_off / 100) * unit_price
#             else:
#                 offer = None
#                 per_ticket_discount = 0.0

#             final_price_per_ticket = unit_price - per_ticket_discount

#             tickets_out[typ] = TicketCategoryDetail(
#                 ticket_ids=ids,
#                 count=count,
#                 unit_price=unit_price,
#                 offer=offer,
#                 discount_per_ticket=per_ticket_discount,
#                 final_price_per_ticket=final_price_per_ticket
#             )

#             total_before += subtotal
#             total_savings += per_ticket_discount * count
#         else:
#             tickets_out[typ] = TicketCategoryDetail(
#                 ticket_ids=[],
#                 count=0,
#                 unit_price=0.0,
#                 offer=None,
#                 discount_per_ticket=0.0,
#                 final_price_per_ticket=0.0
#             )

#     total_after = total_before - total_savings

#     # 5. Persist order record
#     selected_ids = tickets_out['regular'].ticket_ids + tickets_out['vip'].ticket_ids
#     discount_ids = [
#         obj.id for obj, _ in (
#             [(apply_discount(db, payload.event_id, typ, tickets_out[typ].count, 0)[0], None)
#              for typ in ('regular','vip')] if False else []
#         ) if obj
#     ]
#     # note: above is dummy; order_utils.create_order_record only stores the first discount ID,
#     # you can pass both or just one—here we pass all that exist
#     order = create_order_record(
#         payload,
#         selected_ids,
#         total_before,
#         total_after,
#         discount_ids,
#         db
#     )

#     # 6. Return
#     return OrderResponse(
#         message='Your order was successful.',
#         order_id=order.id,
#         user=UserOut(name=payload.user_name, email=payload.user_email),
#         tickets=TicketsOut(**tickets_out),
#         total=OrderTotal(
#             before_discount=total_before,
#             savings=total_savings,
#             after_discount=total_after
#         )
#     )

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
        payload.tickets.dict(),
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
