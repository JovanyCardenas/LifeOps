import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from .models import Requirement, DashboardWidget, Message

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
