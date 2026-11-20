import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from .models import Requirement, DashboardWidget, Message, InventoryChange, InventoryItem
from decimal import Decimal

pytestmark=pytest.mark.django_db

def test_landing_page(client):
    assert client.get(reverse('landing')).status_code==200

def test_dashboard_requires_login(client):
    response=client.get(reverse('dashboard'))
    assert response.status_code==302 and '/accounts/login/' in response.url

def test_dashboard_only_shows_current_user_data(client):
    a=User.objects.create_user('a',password='pass12345'); b=User.objects.create_user('b',password='pass12345')
    Requirement.objects.create(user=a,title='A private task'); Requirement.objects.create(user=b,title='B secret task')
    client.login(username='a',password='pass12345')
    html=client.get(reverse('dashboard')).content.decode()
    assert 'A private task' in html and 'B secret task' not in html

def test_seed_demo_creates_login_ready_account(client):
    call_command('seed_demo')
    assert client.login(username='demo',password='DemoPass123!')
    assert Requirement.objects.filter(user__username='demo').exists()

def test_user_can_create_requirement(client):
    user=User.objects.create_user('owner',password='pass12345'); client.login(username='owner',password='pass12345')
    response=client.post(reverse('module_add',kwargs={'module':'requirements'}),{'title':'New task','category':'task','due_at':'','completed':'','notes':'hello'})
    assert response.status_code==302
    assert Requirement.objects.filter(user=user,title='New task').exists()

def test_user_can_edit_own_record(client):
    user=User.objects.create_user('owner',password='pass12345'); item=Requirement.objects.create(user=user,title='Old',category='task')
    client.login(username='owner',password='pass12345')
    response=client.post(reverse('module_edit',kwargs={'module':'requirements','pk':item.pk}),{'title':'Updated','category':'task','due_at':'','notes':'','completed':''})
    assert response.status_code==302
    item.refresh_from_db(); assert item.title=='Updated'

def test_user_cannot_edit_another_users_record(client):
    a=User.objects.create_user('a',password='pass12345'); b=User.objects.create_user('b',password='pass12345')
    item=Requirement.objects.create(user=b,title='Private',category='task')
    client.login(username='a',password='pass12345')
    assert client.get(reverse('module_edit',kwargs={'module':'requirements','pk':item.pk})).status_code==404

def test_user_can_delete_own_record(client):
    user=User.objects.create_user('owner',password='pass12345'); item=Requirement.objects.create(user=user,title='Delete me',category='task')
    client.login(username='owner',password='pass12345')
    assert client.post(reverse('module_delete',kwargs={'module':'requirements','pk':item.pk})).status_code==302
    assert not Requirement.objects.filter(pk=item.pk).exists()

def test_widget_settings_update_visibility_and_order(client):
    user=User.objects.create_user('owner',password='pass12345'); client.login(username='owner',password='pass12345')
    client.get(reverse('dashboard'))
    widget=DashboardWidget.objects.filter(user=user).first()
    client.post(reverse('dashboard_settings'),{f'position_{widget.id}':'8'})
    widget.refresh_from_db(); assert widget.position==8 and widget.visible is False

def test_message_privacy(client):
    a=User.objects.create_user('a',password='pass12345'); b=User.objects.create_user('b',password='pass12345'); c=User.objects.create_user('c',password='pass12345')
    Message.objects.create(sender=b,recipient=c,body='Secret message')
    Message.objects.create(sender=b,recipient=a,body='Hello A')
    client.login(username='a',password='pass12345')
    html=client.get(reverse('messages_page')).content.decode()
    assert 'Hello A' in html and 'Secret message' not in html

def inventory_url(action, item=None):
    kwargs = {"module": "inventory"}
    if item is not None:
        kwargs["pk"] = item.pk
    return reverse(f"module_{action}", kwargs=kwargs)


def egg_form(quantity, *, revision=None):
    data = {
        "name": "Eggs",
        "location": "Fridge",
        "quantity": quantity,
        "reorder_threshold": "2",
        "is_food": "on",
        "unit": "count",
    }
    if revision is not None:
        data["revision"] = revision
    return data


def test_inventory_add_edit_and_undo(client):
    owner = User.objects.create_user("owner")
    client.force_login(owner)

    response = client.post(inventory_url("add"), egg_form("12"))
    assert response.status_code == 302

    item = InventoryItem.objects.get(user=owner, name="Eggs")
    added = InventoryChange.objects.get(user=owner, item=item, action="add")
    assert added.before == {}
    assert Decimal(added.after["quantity"]) == Decimal("12")

    response = client.post(
        inventory_url("edit", item),
        egg_form("10", revision=item.revision),
    )
    assert response.status_code == 302

    item.refresh_from_db()
    assert item.quantity == Decimal("10")
    edit = InventoryChange.objects.get(user=owner, item=item, action="edit")
    assert Decimal(edit.before["quantity"]) == Decimal("12")
    assert Decimal(edit.after["quantity"]) == Decimal("10")
    assert edit.item_revision == item.revision

    response = client.get(reverse("inventory_activity"))
    assert response.status_code == 200
    assert b"Eggs" in response.content

    undo_url = reverse("inventory_undo", kwargs={"pk": edit.pk})
    assert client.post(undo_url).status_code == 302

    item.refresh_from_db()
    assert item.quantity == Decimal("12")
    assert InventoryChange.objects.filter(
        user=owner, item=item, action="undo", undoes=edit
    ).count() == 1

    assert client.post(undo_url).status_code == 400
    assert InventoryChange.objects.filter(undoes=edit).count() == 1


def test_inventory_archive_hides_item_and_undo_restores_it(client):
    owner = User.objects.create_user("owner")
    client.force_login(owner)
    item = InventoryItem.objects.create(
        user=owner, name="Archive Test Eggs", quantity=12
    )

    archive_url = inventory_url("delete", item)
    assert client.get(archive_url).status_code == 200
    item.refresh_from_db()
    assert item.archived is False

    assert client.post(
        archive_url, {"revision": item.revision}
    ).status_code == 302

    item.refresh_from_db()
    assert item.archived is True
    assert b"Archive Test Eggs" not in client.get(inventory_url("list")).content

    change = InventoryChange.objects.get(user=owner, item=item, action="archive")
    assert change.before["archived"] is False
    assert change.after["archived"] is True

    undo_url = reverse("inventory_undo", kwargs={"pk": change.pk})
    assert client.post(undo_url).status_code == 302

    item.refresh_from_db()
    assert item.archived is False
    assert b"Archive Test Eggs" in client.get(inventory_url("list")).content


def test_inventory_and_activity_are_private(client):
    owner = User.objects.create_user("owner")
    other = User.objects.create_user("other")
    client.force_login(owner)
    data = egg_form("12")
    data["name"] = "Owner Only Eggs"
    assert client.post(inventory_url("add"), data).status_code == 302

    item = InventoryItem.objects.get(user=owner)
    change = InventoryChange.objects.get(user=owner, item=item)
    client.force_login(other)

    for url in (inventory_url("list"), reverse("inventory_activity")):
        response = client.get(url)
        assert response.status_code == 200
        assert b"Owner Only Eggs" not in response.content

    payload = egg_form("1", revision=item.revision)
    assert client.post(inventory_url("edit", item), payload).status_code == 404
    assert client.post(inventory_url("delete", item), payload).status_code == 404
    undo_url = reverse("inventory_undo", kwargs={"pk": change.pk})
    assert client.post(undo_url).status_code == 404

    item.refresh_from_db()
    assert item.quantity == Decimal("12")
    assert item.archived is False
    assert InventoryChange.objects.filter(item=item).count() == 1


def test_inventory_rejects_stale_edit_and_stale_undo(client):
    owner = User.objects.create_user("owner")
    client.force_login(owner)
    item = InventoryItem.objects.create(user=owner, name="Eggs", quantity=12)
    edit_url = inventory_url("edit", item)
    original_revision = item.revision

    assert client.post(
        edit_url, egg_form("10", revision=original_revision)
    ).status_code == 302
    first_edit = InventoryChange.objects.get(item=item)
    item.refresh_from_db()

    assert client.post(
        edit_url, egg_form("8", revision=item.revision)
    ).status_code == 302

    response = client.post(edit_url, egg_form("3", revision=original_revision))
    assert response.status_code == 200
    assert b"This item changed" in response.content

    undo_url = reverse("inventory_undo", kwargs={"pk": first_edit.pk})
    assert client.post(undo_url).status_code == 400

    item.refresh_from_db()
    assert item.quantity == Decimal("8")
    assert InventoryChange.objects.filter(item=item).count() == 2


def test_inventory_rejects_negative_quantity(client):
    owner = User.objects.create_user("owner")
    client.force_login(owner)

    response = client.post(inventory_url("add"), egg_form("-1"))
    assert response.status_code == 200
    assert b"Quantity must be zero or more." in response.content
    assert not InventoryItem.objects.filter(user=owner).exists()
    assert not InventoryChange.objects.filter(user=owner).exists()