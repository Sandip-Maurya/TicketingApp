import pytest
from fastapi.testclient import TestClient
from app.main import app   # adjust import path if your FastAPI app is defined elsewhere

client = TestClient(app)

@pytest.mark.parametrize("payload", [
    {
        "event_id": 1,
        "tickets": {"regular": 2, "vip": 1},
        "user_name": "Alice",
        "user_email": "alice@example.com"
    },
])
def test_reserve_tickets_success(payload):
    response = client.post("/reserve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reservation_id" in data
    assert data["status"] == "reserved"
    # verify counts match
    assert data["tickets"]["regular"]["count"] == payload["tickets"]["regular"]
    assert data["tickets"]["vip"]["count"] == payload["tickets"]["vip"]

def test_reserve_tickets_event_not_found():
    payload = {
        "event_id": 9999,
        "tickets": {"regular": 1},
        "user_name": "Bob",
        "user_email": "bob@example.com"
    }
    response = client.post("/reserve", json=payload)
    assert response.status_code == 404

def test_confirm_reservation_success():
    # First reserve
    payload = {
        "event_id": 1,
        "tickets": {"regular": 1},
        "user_name": "Carol",
        "user_email": "carol@example.com"
    }
    res = client.post("/reserve", json=payload)
    reservation_id = res.json()["reservation_id"]

    # Then confirm
    response = client.post(f"/confirm/{reservation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"

def test_confirm_without_reservation():
    response = client.post("/confirm/9999")
    assert response.status_code == 404

def test_cancel_reservation_success():
    # Reserve then cancel
    payload = {
        "event_id": 1,
        "tickets": {"vip": 1},
        "user_name": "Dave",
        "user_email": "dave@example.com"
    }
    res = client.post("/reserve", json=payload)
    reservation_id = res.json()["reservation_id"]

    response = client.post(f"/cancel/{reservation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"

def test_cancel_after_confirm():
    # Reserve and confirm, then attempt to cancel
    payload = {
        "event_id": 1,
        "tickets": {"regular": 1},
        "user_name": "Eve",
        "user_email": "eve@example.com"
    }
    res = client.post("/reserve", json=payload)
    reservation_id = res.json()["reservation_id"]
    client.post(f"/confirm/{reservation_id}")

    response = client.post(f"/cancel/{reservation_id}")
    assert response.status_code == 400
    assert "cannot cancel" in response.json().get("detail", "").lower()
