from django.urls import path
from . import views
urlpatterns=[
 path('',views.landing,name='landing'),
 path('demo/',views.demo_login,name='demo_login'),
 path('signup/',views.signup,name='signup'),
 path('profile/',views.profile_settings,name='profile_settings'),
 path('dashboard/',views.dashboard,name='dashboard'),
 path('dashboard/settings/',views.dashboard_settings,name='dashboard_settings'),
 path('messages/',views.messages_page,name='messages_page'),
 path('<str:module>/',views.ModuleListView.as_view(),name='module_list'),
 path('<str:module>/add/',views.ModuleCreateView.as_view(),name='module_add'),
 path('<str:module>/<int:pk>/edit/',views.ModuleUpdateView.as_view(),name='module_edit'),
 path('<str:module>/<int:pk>/delete/',views.ModuleDeleteView.as_view(),name='module_delete'),
]
