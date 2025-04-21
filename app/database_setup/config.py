# ./app/database_setup/config.py

from datetime import datetime

# Sample Event Data with Ticket Info Included
IPL_DATETIME = datetime(2025, 4, 22, 19, 30, 0)
COMEDY_SHOW_DATETIME = datetime(2025, 4, 22, 20, 0, 0)
VALID_TILL = datetime(2025, 4, 22, 0, 0, 0)

EVENTS = [
    {
        "name": "LSG vs DC - IPL Match",
        "venue": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow",
        "event_datetime": IPL_DATETIME,
        "description": "IPL Match between Lucknow Super Giants and Delhi Capitals in Lucknow",
        "tickets": {
            "regular": {"count": 900, "price": 1000},
            "vip": {"count": 100, "price": 3000}
        }
    },
    {
        "name": "Comedy Show",
        "venue": "Delhi Theatre, Delhi",
        "event_datetime": COMEDY_SHOW_DATETIME,
        "description": "Stand-up comedy night with top comedians.",
        "tickets": {
            "regular": {"count": 400, "price": 500},
            "vip": {"count": 100, "price": 1000}
        }
    }
]

TICKET_TYPES = ["regular", "vip"]


DISCOUNT_OFFERS = [
    {
        "name": "Group Saver",
        "percentage_off": 10,
        "min_tickets": 5,
        "applicable_ticket_types": "regular",
        "applicable_events": [1, 2],
        "valid_till": VALID_TILL
    },
    {
        "name": "VIP Treat",
        "percentage_off": 15,
        "min_tickets": 3,
        "applicable_ticket_types": "vip",
        "applicable_events": [1],
        "valid_till": VALID_TILL
    },
    {
        "name": "Mega Combo",
        "percentage_off": 20,
        "min_tickets": 6,
        "applicable_ticket_types": "both",
        "applicable_events": [1, 2],
        "valid_till": VALID_TILL
    },
]

