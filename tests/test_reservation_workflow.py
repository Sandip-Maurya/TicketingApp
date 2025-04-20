import pytest
from fastapi.testclient import TestClient
from app.main import app  

import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture(scope="module")
def endpoints():
    return {
        "reserve": "/order/reserve",
        "confirm": "/order/{order_id}/confirm",
        "cancel":  "/order/{order_id}/cancel",
    }

def extract_id(json_data):
    return json_data.get("order_id") or json_data.get("id")

@pytest.mark.parametrize("payload", [
    {
        "event_id": 1,
        "tickets": {"regular": 2, "vip": 1},
        "user_name": "Alice",
        "user_email": "alice@example.com"
    },
])
def test_reserve_tickets_success(endpoints, payload):
    res = client.post(endpoints["reserve"], json=payload)
    # reservation now returns 201 Created
    assert res.status_code == 201, res.text

    data = res.json()
    rid = extract_id(data)
    assert rid, "No order_id in reserve response"

    assert "reserved" in data["message"].lower()
    assert data["tickets"]["regular"]["count"] == payload["tickets"]["regular"]
    assert data["tickets"]["vip"]["count"] == payload["tickets"]["vip"]

def test_reserve_tickets_event_not_found(endpoints):
    payload = {
        "event_id": 9999,
        "tickets": {"regular": 1, "vip": 0},
        "user_name": "Bob",
        "user_email": "bob@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    assert res.status_code == 404

def test_confirm_reservation_success(endpoints):
    # First reserve
    payload = {
        "event_id": 1,
        "tickets": {"regular": 1, "vip": 0},
        "user_name": "Carol",
        "user_email": "carol@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    rid = extract_id(res.json())

    # Then confirm
    confirm_path = endpoints["confirm"].replace("{order_id}", str(rid))
    res2 = client.post(confirm_path)
    assert res2.status_code == 200, res2.text

    data = res2.json()
    assert data["order_id"] == rid
    assert "confirmed" in data["message"].lower()

def test_confirm_without_reservation(endpoints):
    bad = endpoints["confirm"].replace("{order_id}", "9999")
    res = client.post(bad)
    assert res.status_code == 404

def test_cancel_reservation_success(endpoints):
    # First reserve
    payload = {
        "event_id": 1,
        "tickets": {"regular": 0, "vip": 1},
        "user_name": "Dave",
        "user_email": "dave@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    rid = extract_id(res.json())

    # Then cancel
    cancel_path = endpoints["cancel"].replace("{order_id}", str(rid))
    res2 = client.post(cancel_path)
    assert res2.status_code == 200, res2.text

    data = res2.json()
    assert data["order_id"] == rid
    assert "cancelled" in data["message"].lower()

def test_cancel_after_confirm(endpoints):
    # Reserve & confirm
    payload = {
        "event_id": 1,
        "tickets": {"regular": 1, "vip": 0},
        "user_name": "Eve",
        "user_email": "eve@example.com"
    }
    res = client.post(endpoints["reserve"], json=payload)
    rid = extract_id(res.json())
    client.post(endpoints["confirm"].replace("{order_id}", str(rid)))

    # Now cancel—your implementation still allows it
    cancel_path = endpoints["cancel"].replace("{order_id}", str(rid))
    res2 = client.post(cancel_path)
    assert res2.status_code == 200, res2.text

    data = res2.json()
    assert "cancelled" in data["message"].lower()
