# app/main.py

from fastapi import FastAPI
from app.api import events, orders

app = FastAPI()

app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(orders.router, prefix="/order", tags=["Orders"])

@app.get("/")
def read_root():
    return {"message": "Hello From TicketingApp!"}
