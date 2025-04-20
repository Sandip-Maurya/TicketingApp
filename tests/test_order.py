# tests/test_order.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
ENDPOINT = "/order/"  # include trailing slash if that's how your router is defined

# Three valid scenarios: no discount, per‑type discounts, combined discount
valid_success_cases = [
    {"event_id": 1, "tickets": {"regular": 1, "vip": 1},
     "user_name": "Alice", "user_email": "alice@example.com"},
    {"event_id": 1, "tickets": {"regular": 5, "vip": 3},
     "user_name": "Bob", "user_email": "bob@example.com"},
    {"event_id": 1, "tickets": {"regular": 6, "vip": 3},
     "user_name": "Carol", "user_email": "carol@example.com"},
]

@pytest.mark.parametrize("payload", valid_success_cases)
def test_order_success(payload):
    """Valid orders should return 201 Created and correct structure."""
    resp = client.post(ENDPOINT, json=payload)
    assert resp.status_code == 201, resp.text

    data = resp.json()
    # top‑level keys
    assert set(data.keys()) == {"message", "order_id", "user", "tickets", "total", "applied_offers"}

    # message
    assert isinstance(data["message"], str)

    # order_id
    assert isinstance(data["order_id"], int)

    # user block
    assert data["user"] == {"name": payload["user_name"], "email": payload["user_email"]}

    # tickets block
    tickets = data["tickets"]
    assert set(tickets.keys()) == {"regular", "vip"}
    for ttype, block in tickets.items():
        expected = {
            "ticket_ids",
            "count",
            "unit_price",
            "offer",
            "discount_per_ticket",
            "final_price_per_ticket",
        }
        assert set(block.keys()) == expected
        assert isinstance(block["ticket_ids"], list)
        assert all(isinstance(i, int) for i in block["ticket_ids"])
        assert isinstance(block["count"], int)
        assert isinstance(block["unit_price"], (int, float))
        # offer may be None or a string
        assert block["offer"] is None or isinstance(block["offer"], str)
        assert isinstance(block["discount_per_ticket"], (int, float))
        assert isinstance(block["final_price_per_ticket"], (int, float))

    # total block
    total = data["total"]
    assert set(total.keys()) == {"before_discount", "savings", "after_discount"}
    for key in total:
        assert isinstance(total[key], (int, float))

    # applied_offers is a list of strings
    assert isinstance(data["applied_offers"], list)
    assert all(isinstance(o, str) for o in data["applied_offers"])


def test_order_too_many_tickets():
    """Requesting more tickets than available should return 400 or 422 with a detail message."""
    payload = {
        "event_id": 1,
        "tickets": {"regular": 1000, "vip": 2},
        "user_name": "X",
        "user_email": "x@example.com"
    }
    resp = client.post(ENDPOINT, json=payload)
    # your implementation may return 400 or 422 here
    assert resp.status_code in (400, 422), resp.text

    body = resp.json()
    assert "detail" in body and isinstance(body["detail"], str)
    assert "Only" in body["detail"] and "tickets available" in body["detail"]


def test_order_event_not_found():
    """Non‑existent event_id should return 404."""
    payload = {
        "event_id": 9999,
        "tickets": {"regular": 1, "vip": 1},
        "user_name": "Y",
        "user_email": "y@example.com"
    }
    resp = client.post(ENDPOINT, json=payload)
    assert resp.status_code == 404


@pytest.mark.parametrize("bad_payload", [
    {},  # empty
    {"event_id": 1},  # missing tickets & user
    {"tickets": {"regular": 1}},  # missing event_id & user
    {"event_id": "one", "tickets": {"regular":1}, "user_name":"Z", "user_email":"z@z"},  # wrong event_id type
    {"event_id": 1, "tickets": {"gold": 1}, "user_name":"Z", "user_email":"z@z"},        # invalid ticket type
    {"event_id": 1, "tickets": {"regular": -1}, "user_name":"Z", "user_email":"z@z"},     # negative count
    {"event_id": 1, "tickets": {"regular":1, "vip":1}, "user_name":"", "user_email":"z@z"},  # empty name
    {"event_id": 1, "tickets": {"regular":1, "vip":1}, "user_name":"Z", "user_email":""},    # empty email
])
def test_order_validation_errors(bad_payload):
    """Invalid payloads must return 422 Unprocessable Entity."""
    resp = client.post(ENDPOINT, json=bad_payload)
    assert resp.status_code == 422
