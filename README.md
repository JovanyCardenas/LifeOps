# LifeOps

LifeOps is a Django full-stack dashboard for managing daily operations across school, work, money, wellness, meals, career planning, inventory, and shared messages.

The project is designed as a portfolio-grade application: private user data, a demo account, realistic seed data, tests, and a roadmap that can grow into a serious product.

## Features in the MVP

- User login with private dashboard data
- Public landing page and demo account flow
- Work, school, and personal schedule tracking
- Requirement tracking for assignments, bills, and tasks
- Habit and streak tracking
- Budget categories and debt overview
- Meal and recipe planning
- Job application tracking
- Inventory tracking with low-stock counts
- Simple user-to-user messages
- Admin panel for managing records
- Seed command for demo data
- Pytest coverage for core flows

## Demo Account

After setup, run the seed command and use:

- Username: `demo`
- Password: `DemoPass123!`

## Tech Stack

- Python 3.11+
- Django 5.2
- SQLite for local development
- Pytest and pytest-django
- Plain Django templates and CSS

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

## Run Tests

```bash
pytest
```

With coverage:

```bash
coverage run -m pytest
coverage report
```

## Project Direction

The long-term goal is to become a calm command center for students, workers, and busy households. LifeOps should feel more like an official operations product than a toy dashboard: simple navigation, clear permissions, useful defaults, strong empty states, and reliable tests.

See [ROADMAP.md](ROADMAP.md) for planned milestones.
