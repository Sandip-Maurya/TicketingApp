# ./app/database_setup/model.py

from sqlalchemy import (
    Column, 
    Integer, 
    Float, 
    String, 
    Boolean, 
    DateTime, 
    Enum, 
    ForeignKey, 
    func
)
from sqlalchemy.types import JSON
from app.database_setup.database import Base
import enum

# Set Enum for ticket types, order status and discount applicability
class TicketTypes(enum.Enum):
    regular = 'regular'
    vip = 'vip'

class OrderStatus(enum.Enum):
    confirmed = 'confirmed'
    cancelled = 'cancelled'

class DiscountApplicability(enum.Enum):
    regular = 'regular'
    vip = 'vip'
    both = 'both'


# Database model for Event, Ticket, Order and Discount

class Event(Base):
    __tablename__  = 'events'
    id = Column(Integer, primary_key = True, autoincrement = True, index = True)
    name = Column(String, nullable = False)
    venue = Column(String, nullable=False)
    event_datetime = Column(DateTime, nullable = False)
    description = Column(String)
    available_ticket_types = Column(JSON, nullable=False, default=['regular', 'vip'])


class Ticket(Base):
    __tablename__  = 'tickets'
    id = Column(Integer, primary_key = True, autoincrement = True, index = True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable = False)
    price = Column(Float, nullable = False)
    ticket_type = Column(Enum(TicketTypes), nullable = False)
    is_sold = Column(Boolean, default = False, nullable = False)
    issued_to = Column(String, nullable = True)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key = True, autoincrement = True, index = True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable = False)
    sold_tickets_ids = Column(JSON, nullable = False)
    quantity_sold = Column(Integer, nullable = False)
    total_tickets_price = Column(Float, nullable = False)
    price_after_discount = Column(Float, nullable = False)
    applied_discount_id = Column(Integer, ForeignKey('discounts.id'))
    status = Column(Enum(OrderStatus), nullable = False)
    user_name = Column(String, nullable = False)
    user_email = Column(String)
    created_at = Column(DateTime, default = func.now())

class Discount(Base):
    __tablename__ = 'discounts'
    id = Column(Integer, primary_key = True, index = False)
    name = Column(String, nullable = False)
    percentage_off = Column(Integer, nullable = False) # from 0% to 50%
    min_tickets = Column(Integer, nullable = False)
    applicable_ticket_types = Column(Enum(DiscountApplicability), nullable = False)
    applicable_events = Column(JSON, nullable=False)  # NEW: list of event IDs
    valid_till = Column(DateTime)