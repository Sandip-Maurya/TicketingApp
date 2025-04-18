# ./app/database_setup/config.py

from datetime import datetime

# Sample Event Data with Ticket Info Included
EVENTS = [
    {
        "name": "LSG vs DC - IPL Match",
        "venue": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow",
        "event_datetime": datetime(2025, 4, 22, 19, 30, 0),
        "description": "IPL Match between Lucknow Super Giants and Delhi Capitals in Lucknow",
        "tickets": {
            "regular_ticket": {"count": 900, "price": 1000},
            "vip_ticket": {"count": 100, "price": 3000}
        }
    },
    {
        "name": "Comedy Show",
        "venue": "Delhi Theatre, Delhi",
        "event_datetime": datetime(2025, 4, 22, 20, 0, 0),
        "description": "Stand-up comedy night with top comedians.",
        "tickets": {
            "regular_ticket": {"count": 400, "price": 500},
            "vip_ticket": {"count": 100, "price": 1000}
        }
    }
]

TICKET_TYPES = ["regular_ticket", "vip_ticket"]
