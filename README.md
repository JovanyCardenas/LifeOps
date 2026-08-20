# LifeOps

LifeOps is a multi-user personal operations dashboard built with Django. It combines daily planning, school/work requirements, budgeting, debt, habits, meals, career tracking, household inventory, and private messaging in one clean workspace.

## Highlights

- Private per-user data with ownership-safe CRUD
- Customizable dashboard widgets with visibility and ordering
- Schedule, requirements, habits, budget, debt, meals, career, and inventory modules
- Private direct messaging between users
- Responsive enterprise-style sidebar UI
- Realistic portfolio demo account and seed command
- pytest ownership, privacy, CRUD, dashboard, and demo tests
- SQLite for local development; architecture is ready for PostgreSQL

## Demo

- Username: `demo`
- Password: `DemoPass123!`

You can also use the **Open demo** button on the public landing page after running `seed_demo`.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\\Scripts\\activate    # Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Tests

```bash
pytest
coverage run -m pytest
coverage report
```

## Architecture

The MVP deliberately uses one Django app, `core`, so reviewers can understand the project quickly. Domain models are user-owned and all update/delete querysets are filtered by `request.user`. When the project grows, the domains can be split into apps such as `finance`, `planning`, `career`, `wellness`, and `inventory`.

## Production direction

Before deploying publicly, use environment-managed secrets, PostgreSQL, HTTPS, secure cookie settings, WhiteNoise or a CDN for static assets, and a production WSGI/ASGI server. Replace the automatic demo-login route with an isolated read-only demo or resettable demo environment if public writes are undesirable.

See [ROADMAP.md](ROADMAP.md) and [docs/GITHUB_ISSUES.md](docs/GITHUB_ISSUES.md).
