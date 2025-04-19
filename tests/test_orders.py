# tests/test_orders.py

from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture
def basic_payload():
    return {
        "event_id": 1,
        "tickets": {
            "regular": 2,
            'vip': 1    
        },
        "user_name": "Sandip",
        "user_email": "sandip@example.com"
    }
def test_create_order_without_discount(basic_payload):
    response = client.post("/order/", json=basic_payload)
    assert response.status_code == 200
    data = response.json()
    assert "order_id" in data
    assert data["discount_applied"] == []

def test_order_with_combined_discount():
    payload = {
        'event_id': 1,
        'tickets': {
            'regular': 4,
            'vip': 3
        },
        'user_name': 'Combo User',
        'user_email': 'combo@example.com'
    }
    response = client.post('/order/', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert 'order_id' in data
    assert len(data['ticket_ids']) == 7
    assert data['strategy_used'] == 'combined'
    assert data['discount_applied'][0]['name'] == 'Mega Combo'

def test_order_with_separate_discounts():
    payload = {
        'event_id': 1,
        'tickets': {
            'regular': 6
        },
        'user_name': 'Regular Saver',
        'user_email': 'reg@example.com'
    }
    response = client.post('/order/', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data['ticket_ids']) == 6
    assert data['strategy_used'] == 'separate'
    assert data['discount_applied']  == True 


def test_order_with_vip_discount():
    payload = {
        'event_id': 1,
        'tickets': {
            'vip': 3  
        },
        'user_name': 'VIP User',
        'user_email': 'vip@example.com'
    }
    response = client.post('/order/', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data['strategy_used'] == 'separate'
    assert len(data['ticket_ids']) == 3
    assert data['discount_applied'][0]['name'] == 'VIP Treat'

def test_order_with_combined_vs_separate_discount_better_combined():
    payload = {
        'event_id': 1,
        'tickets': {
            'regular': 4,
            'vip': 2  
        },
        'user_name': 'Combo Win',
        'user_email': 'combo_win@example.com'
    }
    response = client.post('/order/', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data['strategy_used'] == 'combined'
    assert len(data['ticket_ids']) == 6
    assert data['discount_applied'][0]['name'] == 'Mega Combo'

def test_order_without_enough_regular_tickets():
    payload = {
        'event_id': 1,
        'tickets': {
            'regular': 9999
        },
        'user_name': 'Overask',
        'user_email': 'overask@example.com'
    }
    response = client.post('/order/', json=payload)
    assert response.status_code == 422
    data = response.json()
    assert 'Only' in data['detail']

def test_order_with_empty_ticket_dict():
    payload = {
        'event_id': 1,
        'tickets': {},
        'user_name': 'Empty',
        'user_email': 'empty@example.com'
    }
    response = client.post('/order/', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['ticket_ids'] == []

def test_order_with_invalid_ticket_type_key():
    payload = {
        'event_id': 1,
        'tickets': {
            'platinum': 2  # invalid key
        },
        'user_name': 'WrongType',
        'user_email': 'wrong@example.com'
    }
    response = client.post('/order/', json=payload)
    assert response.status_code == 422

    data = response.json()
    assert any(
        err['msg'] == "Input should be 'regular' or 'vip'"
        for err in data['detail']
    )
