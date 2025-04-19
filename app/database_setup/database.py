# ./app/database_setup/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Config db
# DATABASE_URL = 'sqlite://' # for in memory db
DATABASE_URL = 'sqlite:///TicketingApp.db'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

# Get the database session for API functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()