# tests/test_events.py

from fastapi.testclient import TestClient
import pytest
from app.main import app 

client = TestClient(app)

@pytest.fixture
def event_response():
    return client.get('/events')

@pytest.fixture
def single_event_response():
    return client.get('/events/2')

@pytest.fixture
def tickets_response():
    return client.get('/events/1/tickets')

def test_get_events_is_response_code_ok(event_response):
    assert event_response.status_code == 200 

def test_get_events_does_response_returns_list(event_response):
    assert isinstance(event_response.json(), list)

def test_get_events_does_response_have_atleast_one_event(event_response):
    assert len(event_response.json()) > 0

def test_get_events_does_response_have_expected_keys(event_response):
    event = event_response.json()[0]
    assert 'name' in event
    assert 'venue' in event
    assert 'event_datetime' in event

def test_get_single_event_is_status_code_ok(single_event_response):
    assert single_event_response.status_code == 200

def test_get_single_event_is_response_data_ok(single_event_response):
    single_event_data = single_event_response.json()
    assert 'id' in single_event_data
    assert 'name' in single_event_data
    assert 'venue' in single_event_data
    assert 'event_datetime' in single_event_data

def test_get_single_event_does_it_fail_for_invalid_event_id():
    response = client.get('/events/3')
    assert response.status_code == 404
    assert 'not found' in response.json()['detail']

def test_get_tickets_is_status_code_ok(tickets_response):
    assert tickets_response.status_code == 200

def test_get_tickets_is_response_a_list(tickets_response):
    assert isinstance(tickets_response.json(), list)

def test_get_tickets_have_tickets_expected_keys(tickets_response):
    ticket = tickets_response.json()[0]
    expected_keys = {"id", "price", "ticket_type", "is_sold"}
    assert expected_keys.issubset(ticket.keys())

def test_get_tickets_does_it_fail_for_invalid_event_id():
    response = client.get('/events/3/tickets')
    assert response.status_code == 404
    assert 'not available' in response.json()['detail']