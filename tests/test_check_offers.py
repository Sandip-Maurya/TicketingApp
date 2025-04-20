import pytest
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)
ENDPOINT = "/offers/check-offers"  # byte-for-byte match your router

@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"event_id": 1, "tickets": {"regular": 5, "vip": 3}}, 200),
        ({"event_id": 1, "tickets": {"regular": 1, "vip": 1}}, 200),
    ],
)
def test_check_offers_success(payload, expected_status):
    resp = client.post(ENDPOINT, json=payload)
    assert resp.status_code == expected_status, resp.text

    data = resp.json()
    # top-level keys
    assert set(data.keys()) == {"message", "tickets", "total"}

    # message
    assert isinstance(data["message"], str)

    # tickets block
    tickets = data["tickets"]
    assert isinstance(tickets, dict)
    # expect all three types present
    assert set(tickets.keys()) == {"regular", "vip", "combined"}

    for ttype, block in tickets.items():
        # each block must contain these keys
        for key in ("count", "unit_price", "eligible_offers", "selected_offer"):
            assert key in block, f"Missing {key} in {ttype}"
        assert isinstance(block["count"], int)
        # unit_price can be None or number
        assert block["unit_price"] is None or isinstance(block["unit_price"], (int, float))
        assert isinstance(block["eligible_offers"], list)
        sel = block["selected_offer"]
        assert isinstance(sel, dict)
        # inside selected_offer
        for key in ("name", "percentage_off", "discount_per_ticket", "final_price_per_ticket"):
            assert key in sel, f"Missing {key} in selected_offer of {ttype}"
        assert isinstance(sel["name"], str)
        assert isinstance(sel["percentage_off"], (int, float))
        assert isinstance(sel["discount_per_ticket"], (int, float))
        assert sel["final_price_per_ticket"] is None or isinstance(sel["final_price_per_ticket"], (int, float))

    # total block
    total = data["total"]
    assert set(total.keys()) == {"before", "savings", "after"}
    assert isinstance(total["before"], (int, float))
    assert isinstance(total["savings"], (int, float))
    assert isinstance(total["after"], (int, float))


def test_check_offers_not_found_or_invalid_event():
    """Event ID not in DB should return a validation or not-found error."""
    resp = client.post(ENDPOINT, json={"event_id": 9999, "tickets": {"regular": 1}})
    # your implementation returns 422 here
    assert resp.status_code in (422, 404)


@pytest.mark.parametrize(
    "bad_payload",
    [
        {},
        {"event_id": 1},
        {"tickets": {"regular": 1}},
        {"event_id": "one", "tickets": {"regular": 1}},
        {"event_id": 1, "tickets": {"gold": 1}},
        {"event_id": 1, "tickets": {"regular": -5}},
    ],
)
def test_check_offers_validation_errors(bad_payload):
    """Invalid payloads must return 422."""
    resp = client.post(ENDPOINT, json=bad_payload)
    assert resp.status_code == 422
