# 🎟️ TicketingApp

A simple yet powerful event ticketing system built using **FastAPI** and **SQLite**, designed to manage events, tickets, and orders with discount offers.  

---

## 🚀 Project Overview

**TicketingApp** lets users:
- Browse upcoming events
- Check ticket availability
- Place orders for different ticket types (regular / VIP)
- Automatically get the best discount offers applied to their order

This project is ideal for learning or demonstrating FastAPI skills, especially around database integration, request validation, and modular backend design.

---

## 📦 Features

✅ Add, update, or remove events  
✅ Manage ticket inventory (regular & VIP types)  
✅ Apply separate or combo discount strategies  
✅ View unsold ticket status per event  
✅ Clean and modular codebase with SQLAlchemy ORM  
✅ Fully tested with **Pytest**  
✅ Ready for containerization using **Docker** (optional)

---

## 🏗️ Tech Stack

- **Python 3.10+**
- **FastAPI** – API framework  
- **SQLite** – Lightweight database  
- **SQLAlchemy** – ORM for database operations  
- **Pydantic** – Request & response validation  
- **Pytest** – Testing framework  
- **Uvicorn** – ASGI server

---

## 🛠️ Project Structure

```
TicketingApp/
│
├── app/
│   ├── api/                 # Route definitions
│   ├── database_setup/      # DB models and session config
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic (modular)
│   └── main.py              # Entry point of the app
│
├── tests/                   # Unit and integration tests
├── TicketingApp.db          # SQLite database (auto-created)
├── Dockerfile               # For containerization (optional)
└── README.md                # Project documentation
```

---

## ⚙️ Installation & Running

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/TicketingApp.git
cd TicketingApp
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
uvicorn app.main:app --reload
```

Visit your app at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

API Docs available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📚 Sample Endpoints

- `GET /events/get-all-events` – List all events  
- `GET /tickets/show-ticket-status` – Show unsold tickets by event  
- `POST /order/` – Reserve tickets and get best discount  
- `GET /offers/check-offers` – Preview available offers before purchase

---

## ❤️ Contribution

Contributions, issues, and feature requests are welcome!  
Feel free to open a pull request or submit an issue.

---

## 📃 License

This project is licensed under the **MIT License**.

---

## 🙌 Acknowledgments

Built with ❤️ by **Sandip Maurya**  
Thanks to the FastAPI and SQLAlchemy communities for their amazing tools!

---