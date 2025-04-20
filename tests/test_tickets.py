# tests/test_tickets.py

from fastapi.testclient import TestClient
from app.main import app  

client = TestClient(app)

def test_ticket_types_endpoint():
    """GET /tickets/ticket-types should return a list of events with available ticket types."""
    response = client.get('/tickets/ticket-types')
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list), "Response should be a list"
    # It’s valid for the list to be empty, so we don’t force a length check

    for item in data:
        # keys: event_name (str), ticket_types (list[str])
        assert set(item.keys()) == {'event_name', 'ticket_types'}
        assert isinstance(item['event_name'], str)
        assert isinstance(item['ticket_types'], list)
        # each ticket type should be a non-empty string
        for tt in item['ticket_types']:
            assert isinstance(tt, str)
            assert tt, "ticket_types entries must be non-empty strings"

def test_show_ticket_status_endpoint():
    """GET /tickets/show-ticket-status should return per-event counts & prices for each ticket type."""
    response = client.get('/tickets/show-ticket-status')
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for item in data:
        # Must have event_name plus at least 'regular' and 'vip'
        assert 'event_name' in item and isinstance(item['event_name'], str)

        # Check each ticket‐type block
        for ttype in ('regular', 'vip'):
            assert ttype in item, f"Missing '{ttype}' block"
            block = item[ttype]
            assert isinstance(block, dict)
            # Each block must have count (int) and price (int/float)
            assert 'count' in block and isinstance(block['count'], int)
            assert 'price' in block and isinstance(block['price'], (int, float))
