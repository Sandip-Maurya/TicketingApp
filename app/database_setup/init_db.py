# ./app/database_setup/init_db.py

from app.database_setup.database import engine
from app.database_setup.model import Base 
from app.database_setup import model

# Create database
Base.metadata.create_all(bind = engine)