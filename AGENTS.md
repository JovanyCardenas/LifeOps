exit# LifeOps Development Context

LifeOps is a serious multi-user personal operations application, not a toy dashboard.

## Non-negotiable rules

1. Every private domain record must be scoped to the authenticated user.
2. Never fetch an editable/deletable private object from an unscoped model queryset.
3. Add ownership/privacy tests whenever a new private model or route is introduced.
4. Prefer Django conventions and server-rendered forms before adding client-side complexity.
5. Keep visual design compact, calm, accessible, and professional.
6. Avoid decorative gradients, excessive card nesting, and landing-page-style UI inside the application.
7. New features should include empty states, clear actions, validation, and responsive behavior.
8. Seed data should make the demo account realistic while containing no real personal information.
9. Keep the MVP understandable; split apps only when domains become large enough to justify it.
10. Do not commit secrets, the SQLite database, virtual environments, coverage output, or generated static files.

## Verification before merging

```bash
python manage.py check
python manage.py makemigrations --check
pytest
```
