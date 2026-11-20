from django.urls import path
from . import views, inventory_views, inventory_api, inventory_token_views
urlpatterns=[
 path('',views.landing,name='landing'),
 path('demo/',views.demo_login,name='demo_login'),
 path('signup/',views.signup,name='signup'),
 path('profile/',views.profile_settings,name='profile_settings'),
 path('dashboard/',views.dashboard,name='dashboard'),
 path('dashboard/settings/',views.dashboard_settings,name='dashboard_settings'),
 path('messages/',views.messages_page,name='messages_page'),

 path("inventory/add/", inventory_views.InventoryEditor.as_view()),
 path("inventory/<int:pk>/edit/", inventory_views.InventoryEditor.as_view()),
 path("inventory/<int:pk>/delete/", inventory_views.archive_item),
 path("inventory/activity/", inventory_views.inventory_activity,name="inventory_activity"),
 path("inventory/activity/<int:pk>/undo/",inventory_views.undo_inventory_change, name="inventory_undo"),

 path("api/inventory/", inventory_api.inventory_list, name="inventory_api_list"),

 path(
  "api/inventory/changes/",
  inventory_api.inventory_write,
  name="inventory_api_write",
 ),

 path(
  "profile/inventory-access/",
  inventory_token_views.inventory_tokens,
  name="inventory_tokens",
 ),
 path(
  "profile/inventory-access/<int:pk>/revoke/",
  inventory_token_views.revoke_inventory_token,
  name="inventory_token_revoke",
 ),

 path('<str:module>/',views.ModuleListView.as_view(),name='module_list'),
 path('<str:module>/add/',views.ModuleCreateView.as_view(),name='module_add'),
 path('<str:module>/<int:pk>/edit/',views.ModuleUpdateView.as_view(),name='module_edit'),
 path('<str:module>/<int:pk>/delete/',views.ModuleDeleteView.as_view(),name='module_delete'),
]
