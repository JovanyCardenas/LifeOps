import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from .models import DashboardWidget, Requirement


@pytest.mark.django_db
def test_landing_page_renders(client):
    response = client.get(reverse("landing"))

    assert response.status_code == 200
    assert "LifeOps" in response.content.decode()


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboard"))

    assert response.status_code == 302
    assert reverse("login") in response["Location"]


@pytest.mark.django_db
def test_dashboard_only_shows_current_user_data(client):
    owner = User.objects.create_user("owner", password="pass12345")
    other = User.objects.create_user("other", password="pass12345")
    Requirement.objects.create(
        user=owner,
        title="Visible assignment",
        category=Requirement.ASSIGNMENT,
        due_at=timezone.now(),
    )
    Requirement.objects.create(
        user=other,
        title="Private assignment",
        category=Requirement.ASSIGNMENT,
        due_at=timezone.now(),
    )

    client.force_login(owner)
    response = client.get(reverse("dashboard"))
    body = response.content.decode()

    assert response.status_code == 200
    assert "Visible assignment" in body
    assert "Private assignment" not in body


@pytest.mark.django_db
def test_seed_demo_creates_login_ready_demo_account(client):
    call_command("seed_demo")

    assert client.login(username="demo", password="DemoPass123!")
    response = client.get(reverse("dashboard"))
    body = response.content.decode()

    assert response.status_code == 200
    assert "Data Structures lecture" in body
    assert "Chicken rice bowl" in body


@pytest.mark.django_db
def test_user_can_create_requirement_from_frontend(client):
    user = User.objects.create_user("owner", password="pass12345")
    client.force_login(user)

    response = client.post(
        reverse("module_create", args=["requirements"]),
        {
            "title": "Read chapter 4",
            "category": Requirement.ASSIGNMENT,
            "due_at": "2026-09-01T10:30",
            "completed": "",
            "notes": "Bring notes to class.",
        },
    )

    assert response.status_code == 302
    assert Requirement.objects.filter(user=user, title="Read chapter 4").exists()


@pytest.mark.django_db
def test_user_can_edit_and_delete_own_requirement(client):
    user = User.objects.create_user("owner", password="pass12345")
    requirement = Requirement.objects.create(user=user, title="Old title")
    client.force_login(user)

    edit_response = client.post(
        reverse("module_edit", args=["requirements", requirement.pk]),
        {
            "title": "Updated title",
            "category": Requirement.TASK,
            "due_at": "",
            "notes": "",
        },
    )
    requirement.refresh_from_db()

    assert edit_response.status_code == 302
    assert requirement.title == "Updated title"

    delete_response = client.post(reverse("module_delete", args=["requirements", requirement.pk]))

    assert delete_response.status_code == 302
    assert not Requirement.objects.filter(pk=requirement.pk).exists()


@pytest.mark.django_db
def test_user_cannot_edit_another_users_requirement(client):
    owner = User.objects.create_user("owner", password="pass12345")
    other = User.objects.create_user("other", password="pass12345")
    requirement = Requirement.objects.create(user=other, title="Private task")
    client.force_login(owner)

    response = client.get(reverse("module_edit", args=["requirements", requirement.pk]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_dashboard_widget_settings_control_visibility(client):
    user = User.objects.create_user("owner", password="pass12345")
    client.force_login(user)
    client.get(reverse("dashboard"))
    widgets = DashboardWidget.objects.filter(user=user)

    payload = {}
    for widget in widgets:
        payload[f"{widget.key}-position"] = str(widget.position)
        if widget.key != "habits":
            payload[f"{widget.key}-visible"] = "on"

    response = client.post(reverse("dashboard_settings"), payload)
    DashboardWidget.objects.get(user=user, key="habits").refresh_from_db()

    assert response.status_code == 302
    assert DashboardWidget.objects.get(user=user, key="habits").visible is False
