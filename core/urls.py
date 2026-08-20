from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("demo/", views.demo_login, name="demo_login"),
    path("messages/", views.messages, name="messages"),
]
