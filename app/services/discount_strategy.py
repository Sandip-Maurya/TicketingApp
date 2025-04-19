# app/services/discount_strategy.py

from sqlalchemy.orm import Session
from app.database_setup.model import Discount
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from collections import defaultdict
from app.database_setup.model import Discount, DiscountApplicability, Event


def get_best_discount(
    db: Session,
    event_id: int,
    ticket_type: str,
    quantity: int
) -> Optional[Discount]:
    today = datetime.now()

    # Step 1: Load all valid discounts and filter in Python
    discounts = db.query(Discount).filter(
        Discount.valid_till >= today,
        Discount.min_tickets <= quantity
    ).all()

    # Manual filtering since SQLite doesn't support JSON contains properly
    discounts = [d for d in discounts if event_id in d.applicable_events]

    applicable_discounts = []

    for d in discounts:
        if ticket_type == 'both':
            if d.applicable_ticket_types == DiscountApplicability.both:
                applicable_discounts.append(d)
        else:
            if d.applicable_ticket_types.value == ticket_type:
                applicable_discounts.append(d)

        # if ticket_type == 'both':
        #     if d.applicable_ticket_types == DiscountApplicability.both:
        #         applicable_discounts.append(d)
        # else:
        #     if (
        #         d.applicable_ticket_types.value == ticket_type
        #         or d.applicable_ticket_types == DiscountApplicability.both
        #     ):
        #         applicable_discounts.append(d)

    if applicable_discounts:
        return max(applicable_discounts, key=lambda d: d.percentage_off)

    return None

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
    print(f'\n[DEBUG] Total Tickets: {len(tickets)}, Total Price: {total_price}')

    # Option A: Separate Discounts
    price_separate = 0
    discounts_used = []

    print('[DEBUG] Checking separate discounts...')
    for ticket_type, group in grouped.items():
        qty = len(group)
        type_total = sum(t.price for t in group)
        discount = get_best_discount(db, event_id, ticket_type, qty)

        if discount:
            discount_amt = discount.percentage_off / 100 * type_total
            price_separate += type_total - discount_amt
            discounts_used.append(discount)
            print(f' - {ticket_type}: {qty} tickets, Discount: {discount.name}, Off: {discount.percentage_off}%, Saving: {discount_amt}')
        else:
            price_separate += type_total
            print(f' - {ticket_type}: {qty} tickets, No discount.')

    print(f'[DEBUG] Total price after separate discounts: {price_separate}')

    # Option B: Combined Discount
    combined_qty = len(tickets)
    combined_total = total_price
    combo_discount = get_best_discount(db, event_id, 'both', combined_qty)

    if combo_discount:
        combo_price = combined_total * (1 - combo_discount.percentage_off / 100)
        saving = combined_total - combo_price
        print(f'[DEBUG] Combined discount: {combo_discount.name}, Off: {combo_discount.percentage_off}%, Saving: {saving}')
    else:
        combo_price = combined_total
        print('[DEBUG] No combined discount.')

    # Choose better
    if combo_discount and combo_price < price_separate:
        print('[DEBUG] ✅ Choosing COMBINED discount.\n')
        return [combo_discount], combo_price, 'combined'
    else:
        print('[DEBUG] ✅ Choosing SEPARATE discounts.\n')
        return discounts_used, price_separate, 'separate'
