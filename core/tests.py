import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from .models import Requirement


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
