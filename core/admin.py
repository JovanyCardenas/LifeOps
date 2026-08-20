from django.contrib import admin

from .models import (
    BudgetCategory,
    Debt,
    Habit,
    InventoryItem,
    JobApplication,
    MealPlan,
    Message,
    Profile,
    Requirement,
    ScheduleEvent,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "role", "updated_at")


@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "starts_at", "ends_at")
    list_filter = ("category",)
    search_fields = ("title", "location", "user__username")


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "due_at", "completed")
    list_filter = ("category", "completed")
    search_fields = ("title", "notes", "user__username")


admin.site.register(Habit)
admin.site.register(BudgetCategory)
admin.site.register(Debt)
admin.site.register(MealPlan)
admin.site.register(JobApplication)
admin.site.register(InventoryItem)
admin.site.register(Message)

# Register your models here.
