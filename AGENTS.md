# LifeOps Agent Guide

## Product Summary

LifeOps is a full-stack Django application for managing daily life operations. It is aimed at students, workers, and households that need one private dashboard for schedules, assignments, habits, finances, debt, meals, job applications, inventory, and collaboration.

The application should feel like an official enterprise productivity product: calm, useful, simple, and trustworthy. Avoid making the UI look like a generic AI-generated landing page. Prefer practical workflows, clean information hierarchy, compact dashboards, clear tables, and helpful empty states.

## Current Architecture

- `config/` contains Django project settings and root URLs.
- `core/` contains the MVP models, views, templates, static CSS, admin registrations, tests, and management commands.
- `core/models.py` defines user-owned records for the first product modules.
- `core/templates/core/` contains the public landing page, dashboard, messages view, and base layout.
- `core/management/commands/seed_demo.py` creates the demo account and realistic starter data.
- `ROADMAP.md` tracks planned milestones and should be converted into GitHub issues.

## Development Principles

- Every private record must be scoped to the authenticated user unless it is explicitly shared.
- Add tests for ownership, permissions, and validation when adding a new feature.
- Keep UI simple and professional. Use cards for repeated dashboard modules, not for every page section.
- Prefer Django conventions before adding extra packages.
- Keep the MVP modular, but do not split into many Django apps until a module has enough behavior to justify it.
- Demo data should stay realistic and safe to expose publicly.

## Near-Term Build Order

1. Add CRUD pages for requirements and schedule events.
2. Add registration and profile editing.
3. Add CRUD pages for budgets, debts, habits, meals, job applications, and inventory.
4. Add message compose and read-state behavior.
5. Add deployment settings and publish a public demo.
6. Add screenshots and a short case study to the README.

## Testing Expectations

Run:

```bash
pytest
```

For larger changes, also run:

```bash
coverage run -m pytest
coverage report
```

Do not merge a feature that lets users view or mutate another user's private data unless that behavior is part of an explicit sharing feature.

## Demo Account

Use:

- Username: `demo`
- Password: `DemoPass123!`

Refresh demo data with:

```bash
python manage.py seed_demo
```
