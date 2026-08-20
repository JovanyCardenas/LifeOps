from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/settings/", views.dashboard_settings, name="dashboard_settings"),
    path("demo/", views.demo_login, name="demo_login"),
    path("messages/", views.messages, name="messages"),
    path("modules/<slug:slug>/", views.module_list, name="module_list"),
    path("modules/<slug:slug>/add/", views.module_create, name="module_create"),
    path("modules/<slug:slug>/<int:pk>/edit/", views.module_edit, name="module_edit"),
    path("modules/<slug:slug>/<int:pk>/delete/", views.module_delete, name="module_delete"),
]
