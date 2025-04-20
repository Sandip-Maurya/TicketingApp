# tests/test_offers.py

from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from app.main import app  

client = TestClient(app)

def test_get_all_offers():
    """GET /offers/all should return a dict mapping event names to available offers."""
    response = client.get("/offers/all")
    assert response.status_code == 200

    data = response.json()
    # Top‐level must be a dict where keys are event names
    assert isinstance(data, dict), "Response should be a JSON object"

    for event_name, offers in data.items():
        # event_name should be a nonempty string
        assert isinstance(event_name, str) and event_name, "Event name must be a nonempty string"

        # offers should be a dict of offer‐types
        assert isinstance(offers, dict), f"Offers for '{event_name}' should be an object"

        for offer_type, detail in offers.items():
            # offer_type should be one of 'regular','vip','both'
            assert offer_type in {"regular", "vip", "both"}, f"Unexpected offer type '{offer_type}'"

            # detail must include exactly these keys:
            expected_keys = {"name", "percentage_off", "min_tickets", "valid_till"}
            assert set(detail.keys()) == expected_keys, f"{offer_type} detail keys mismatch"

            # validate types
            assert isinstance(detail["name"], str)
            assert isinstance(detail["percentage_off"], (int, float))
            assert isinstance(detail["min_tickets"], int)
            assert isinstance(detail["valid_till"], str)
            # ensure valid_till is YYYY-MM-DD
            try:
                datetime.strptime(detail["valid_till"], "%Y-%m-%d")
            except ValueError:
                pytest.fail(f"valid_till for {offer_type} on {event_name} is not YYYY-MM-DD")

