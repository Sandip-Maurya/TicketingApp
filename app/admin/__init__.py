# app/admin/__init__.py

from fastapi import APIRouter

from app.admin.events_management import router as events_router
from app.admin.tickets_management import router as tickets_router
# from app.admin.discounts_management import router as discounts_router

router = APIRouter()

# mount the sub‑routers under /admin
router.include_router(events_router, prefix='/events', tags=['Admin - Events Management'])
router.include_router(tickets_router, prefix='/events/{event_id}/tickets', tags=['Admin - Tickets Management'])
# router.include_router(discounts_router, prefix='/discounts', tags=['admin-discounts'])
