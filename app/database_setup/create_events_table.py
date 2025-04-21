# app/database_setup/create_events_table.py

from app.database_setup.database import engine
from app.database_setup.model import Event

Event.__table__.create(bind=engine)
print('Event table created successfully.')