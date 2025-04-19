# tests/test_orders.py

from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture
def valid_order_payload():
    return {
        "event_id": 1,
        "quantity": 2,
        "user_name": "Sandip",
        "user_email": "sandip@example.com"
    }

def test_create_order_basic_success(valid_order_payload):
    response = client.post("/order/", json=valid_order_payload)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert "ticket_ids" in data
    assert len(data["ticket_ids"]) == valid_order_payload["quantity"]

def test_create_order_with_discount_applied():
    response = client.post("/order/", json={
        "event_id": 1,
        "quantity": 6,  # Should trigger "Mega Combo"
        "user_name": "TestUser",
        "user_email": "testuser@example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert "order_id" in data
    assert len(data["ticket_ids"]) == 6
    assert data.get("discount_applied") == "Mega Combo"

def test_order_event_does_not_exist():
    response = client.post("/order/", json={
        "event_id": 999,
        "quantity": 1,
        "user_name": "X",
        "user_email": "x@example.com"
    })
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]

def test_order_when_tickets_are_insufficient():
    response = client.post("/order/", json={
        "event_id": 1,
        "quantity": 10000,
        "user_name": "Overflow",
        "user_email": "overflow@example.com"
    })
    assert response.status_code == 404
    assert "tickets available" in response.json()["detail"]
