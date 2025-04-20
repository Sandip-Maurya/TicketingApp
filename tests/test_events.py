# tests/test_events.py

from fastapi.testclient import TestClient
from app.main import app  

client = TestClient(app)

def test_get_all_events():
    response = client.get('/events/get-all-events')
    assert response.status_code == 200
    
    events = response.json()
    
    assert isinstance(events, list), "The response should be a list."

    expected_keys = {'id', 'name', 'venue', 'event_datetime', 'description'}
    for event in events:
        assert expected_keys == set(event.keys()), "Event keys mismatch."
        assert isinstance(event['id'], int), "'id' should be an integer."
        assert isinstance(event['name'], str), "'name' should be a string."
        assert isinstance(event['venue'], str), "'venue' should be a string."
        assert isinstance(event['event_datetime'], str), "'event_datetime' should be a string."
        assert isinstance(event['description'], str), "'description' should be a string."
