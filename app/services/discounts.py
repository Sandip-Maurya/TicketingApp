# ./app/services/discounts.py

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import String, cast 
from app.database_setup.model import Discount, DiscountApplicability

def get_best_discount(
    db: Session,
    event_id: int,
    ticket_type: str,
    quantity: int
) -> Optional[Discount]:
    today = datetime.now()

    # Fetch all active discounts
    discounts = db.query(Discount).filter(
        Discount.valid_till >= today,
        Discount.min_tickets <= quantity,
        cast(Discount.applicable_events, String).like(f"%{event_id}%")
    ).all()

    # Filter based on ticket type
    applicable_discounts = []
    for d in discounts:
        if d.applicable_ticket_types == DiscountApplicability.both:
            applicable_discounts.append(d)
        elif d.applicable_ticket_types.value == ticket_type:
            applicable_discounts.append(d)

    # Return best discount (highest percentage)
    if applicable_discounts:
        return max(applicable_discounts, key=lambda d: d.percentage_off)
    
    return None
