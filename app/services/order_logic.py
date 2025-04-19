# app/services/discount_strategy.py

from sqlalchemy.orm import Session
from app.services.discounts import get_best_discount
from app.database_setup.model import Discount

def get_best_discount_strategy(
    db: Session,
    event_id: int,
    tickets: list  # all reserved Ticket objects
) -> tuple[list[Discount], float, str]:
    """
    Determine whether separate or combined discount gives better price.
    Returns: [applied_discounts], final_price, strategy_used
    """
    from collections import defaultdict
    grouped = defaultdict(list)
    for t in tickets:
        grouped[t.ticket_type.value].append(t)

    total_price = sum(t.price for t in tickets)

    # Option A: Separate discounts
    price_separate = 0
    discounts_used = []

    for ticket_type, group in grouped.items():
        qty = len(group)
        type_total = sum(t.price for t in group)
        discount = get_best_discount(db, event_id, ticket_type, qty)

        if discount:
            discount_amt = discount.percentage_off / 100 * type_total
            price_separate += type_total - discount_amt
            discounts_used.append(discount)
        else:
            price_separate += type_total

    # Option B: Combined discount (treat as a group regardless of type)
    combined_qty = len(tickets)
    combined_total = total_price
    combo_discount = get_best_discount(db, event_id, 'both', combined_qty)

    if combo_discount:
        combo_price = combined_total * (1 - combo_discount.percentage_off / 100)
    else:
        combo_price = combined_total

    # Choose better
    if combo_discount and combo_price < price_separate:
        return [combo_discount], combo_price, 'combined'
    else:
        return discounts_used, price_separate, 'separate'
