# lunch_menu

A Python web application for browsing and searching a restaurant lunch menu. Built with a service-oriented backend structure, database layer, and REST API endpoints.

## Features

- REST API for menu item retrieval and search
- Modular service layer separating business logic from routing
- Database integration for persistent menu storage
- Backend integration tests covering API behaviour
- Static asset serving for frontend resources

## Tech stack

- Python
- Flask / aiohttp
- PostgreSQL (or SQLite for local dev)
- pytest

## Project structure
lunch_menu/
├── app.py              # Application entry point and route definitions
├── run.py              # Server startup
├── search.py           # Search logic
├── services/           # Business logic layer
├── database/           # Database models and queries
├── backend_tests/      # Integration tests
├── resources/          # API resource definitions
├── static/             # Static assets
└── settings.cfg        # Configuration

## Running locally

```bash
pip install -r requirements.txt
python run.py
```

## Running tests

```bash
pytest backend_tests/
```
