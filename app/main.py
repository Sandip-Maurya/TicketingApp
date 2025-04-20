# app/main.py

from fastapi import FastAPI
from app.api import events, orders, offers, tickets
from app.admin import router as admin_router

app = FastAPI(title='TicketingApp')

# Admin endpoints
app.include_router(admin_router)

app.include_router(events.router, prefix="/events", tags=["2. Events"])
app.include_router(orders.router, prefix="/order", tags=["5. Orders"])
app.include_router(offers.router, prefix='/offers', tags=['4. Offers'])
app.include_router(tickets.router, prefix='/tickets', tags=['3. Tickets'])


@app.get("/")
def read_root():
    return {"message": "Hello From TicketingApp!"}
