TOOL_SECTIONS = (
    ("inventory", "Inventory"),
    ("recipes", "Recipes"),
    ("meals", "Meal Plans"),
    ("budget", "Budget"),
    ("debt", "Debt"),
    ("schedule", "Schedule"),
    ("requirements", "Requirements / Tasks"),
    ("habits", "Habits"),
    ("career", "Career"),
    ("messages", "Messages"),
)


def scopes_from_form(form):
    scopes = []
    for key, _ in TOOL_SECTIONS:
        can_write = form.get(f"{key}_write") == "on"
        can_read = form.get(f"{key}_read") == "on"
        if can_read or can_write:
            scopes.append(f"{key}:read")
        if can_write:
            scopes.append(f"{key}:write")
    return scopes


def permission_rows(scopes):
    return [
        {
            "key": key,
            "label": label,
            "read": f"{key}:read" in scopes,
            "write": f"{key}:write" in scopes,
        }
        for key, label in TOOL_SECTIONS
    ]