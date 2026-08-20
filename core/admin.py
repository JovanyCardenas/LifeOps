from django.contrib import admin
from .models import *
for model in [Profile,DashboardWidget,ScheduleEvent,Requirement,Habit,BudgetCategory,Debt,MealPlan,JobApplication,InventoryItem,Message]:
    admin.site.register(model)
