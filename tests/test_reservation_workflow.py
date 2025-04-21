import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import random
from app.main import app
from app.database_setup.database import SessionLocal
from app.database_setup.model import Event, Ticket, TicketTypes

client = TestClient(app)

# -------------- Fixtures --------------

@pytest.fixture(scope="module")
def endpoints():
    return {
        "reserve": "/order/reserve",
        "confirm": "/order/{order_id}/confirm",
        "cancel":  "/order/{order_id}/cancel",
    }

@pytest.fixture(scope="module")
def future_event():
    db = SessionLocal()
    now = datetime.now()

    future = db.query(Event).filter(Event.event_datetime >= now).first()
    if not future:
        future = Event(
            name="Future Test Event",
            event_datetime=now + timedelta(days=2),
            venue="Test Hall A"
        )
        db.add(future)
        db.commit()
        db.refresh(future)

    yield future.id
    db.close()

@pytest.fixture(scope="module")
def expired_event():
    db = SessionLocal()
    now = datetime.now()

    # Create a definitely expired event
    event = Event(
        name="Expired Test Event",
        event_datetime=now - timedelta(days=2),  # firmly in the past
        venue="Old Hall"
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Seed 2 regular and 2 vip unsold & unreserved tickets
    for typ in ['regular', 'vip']:
        for _ in range(2):
            ticket = Ticket(
                event_id=event.id,
                ticket_type=TicketTypes(typ),
                price=1000.0 if typ == 'regular' else 3000.0,
                is_sold=False,
                is_reserved=False
            )
            db.add(ticket)
    db.commit()

    yield event.id
    db.close()

# -------------- Helper --------------

def extract_id(json_data):
    return json_data.get("order_id") or json_data.get("id")

# -------------- Tests --------------
def test_reserve_tickets_success(endpoints, future_event):
    payload = {
        "event_id": future_event,
        "tickets": {"regular": 1, "vip": 0},  # safer for repeatable tests
        "user_name": "Alice",
        "user_email": "alice@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    rid = extract_id(data)
    assert rid
    assert "reserved" in data["message"].lower()

def test_reserve_tickets_event_not_found(endpoints):
    payload = {
        "event_id": 9999,
        "tickets": {"regular": 1, "vip": 0},
        "user_name": "Ghost",
        "user_email": "ghost@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    assert res.status_code == 404

def test_reserve_fails_if_event_expired(endpoints, expired_event):
    from app.database_setup.database import SessionLocal
    from app.database_setup.model import Ticket
    db = SessionLocal()
    available_tickets = db.query(Ticket).filter(
        Ticket.event_id == expired_event,
        Ticket.is_sold == False,
        Ticket.is_reserved == False,
        Ticket.ticket_type == TicketTypes.regular
    ).all()
    print(f"DEBUG: Remaining regular tickets for expired event: {len(available_tickets)}")
    db.close()

    payload = {
        "event_id": expired_event,
        "tickets": {"regular": 1, "vip": 0},  # ✅ fix applied
        "user_name": "Time Traveler",
        "user_email": "old@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    print("DEBUG response:", res.json())

    assert res.status_code == 400
    assert "already started" in res.json()["detail"].lower()




def test_reserve_fails_if_event_expired(endpoints, expired_event):
    from app.database_setup.database import SessionLocal
    from app.database_setup.model import Ticket
    db = SessionLocal()
    available_tickets = db.query(Ticket).filter(
        Ticket.event_id == expired_event,
        Ticket.is_sold == False,
        Ticket.is_reserved == False,
        Ticket.ticket_type == TicketTypes.regular
    ).all()
    print(f"DEBUG: Remaining regular tickets for expired event: {len(available_tickets)}")
    db.close()

    payload = {
        "event_id": expired_event,
        "tickets": {"regular": 1, "vip": 0},  # ✅ fix applied
        "user_name": "Time Traveler",
        "user_email": "old@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    print("DEBUG response:", res.json())

    assert res.status_code == 400
    assert "already started" in res.json()["detail"].lower()


def test_reserve_fails_when_tickets_not_fully_available(endpoints, future_event):
    payload = {
        "event_id": future_event,
        "tickets": {"regular": 9999, "vip": 9999},
        "user_name": "Bulk Buyer",
        "user_email": "fail@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    assert res.status_code == 422
    assert "not enough tickets" in res.json()["detail"].lower()

def test_confirm_reservation_success(endpoints, future_event):
    payload = {
        "event_id": future_event,
        "tickets": {"regular": 1, "vip": 0},
        "user_name": "Carol",
        "user_email": "carol@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    rid = extract_id(res.json())

    confirm_path = endpoints["confirm"].replace("{order_id}", str(rid))
    res2 = client.post(confirm_path)
    assert res2.status_code == 200, res2.text
    data = res2.json()
    assert data["order_id"] == rid
    assert "confirmed" in data["message"].lower()

def test_confirm_without_reservation(endpoints):
    res = client.post(endpoints["confirm"].replace("{order_id}", "9999"))
    assert res.status_code == 404

def test_cancel_reservation_success(endpoints, future_event):
    payload = {
        "event_id": future_event,
        "tickets": {"regular": 1, "vip": 0},  # safer
        "user_name": "Dave",
        "user_email": "dave@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    assert res.status_code == 201, res.text  # NEW assert here

    rid = extract_id(res.json())
    assert rid is not None, "Reservation failed, no order_id returned"

    cancel_path = endpoints["cancel"].replace("{order_id}", str(rid))
    res2 = client.post(cancel_path)
    assert res2.status_code == 200, res2.text
    data = res2.json()
    assert data["order_id"] == rid
    assert "cancelled" in data["message"].lower()


def test_cancel_after_confirm(endpoints, future_event):
    payload = {
        "event_id": future_event,
        "tickets": {"regular": 1, "vip": 0},
        "user_name": "Eve",
        "user_email": "eve@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    rid = extract_id(res.json())

    client.post(endpoints["confirm"].replace("{order_id}", str(rid)))

    cancel_path = endpoints["cancel"].replace("{order_id}", str(rid))
    res2 = client.post(cancel_path)
    assert res2.status_code == 200, res2.text
    data = res2.json()
    assert "cancelled" in data["message"].lower()
