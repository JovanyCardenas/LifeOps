from django import forms

from .models import (
    BudgetCategory,
    DashboardWidget,
    Debt,
    Habit,
    InventoryItem,
    JobApplication,
    MealPlan,
    Message,
    Requirement,
    ScheduleEvent,
)


class BaseStyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault("class", "field-control")


class ScheduleEventForm(BaseStyledModelForm):
    class Meta:
        model = ScheduleEvent
        fields = ["title", "category", "starts_at", "ends_at", "location"]
        widgets = {
            "starts_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "ends_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["starts_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["ends_at"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned = super().clean()
        starts_at = cleaned.get("starts_at")
        ends_at = cleaned.get("ends_at")
        if starts_at and ends_at and ends_at <= starts_at:
            self.add_error("ends_at", "End time must be after start time.")
        return cleaned


class RequirementForm(BaseStyledModelForm):
    class Meta:
        model = Requirement
        fields = ["title", "category", "due_at", "completed", "notes"]
        widgets = {
            "due_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["due_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class HabitForm(BaseStyledModelForm):
    class Meta:
        model = Habit
        fields = ["name", "target_per_week", "current_streak"]


class BudgetCategoryForm(BaseStyledModelForm):
    class Meta:
        model = BudgetCategory
        fields = ["name", "monthly_limit", "current_spend"]


class DebtForm(BaseStyledModelForm):
    class Meta:
        model = Debt
        fields = ["name", "balance", "minimum_payment", "apr"]


class MealPlanForm(BaseStyledModelForm):
    class Meta:
        model = MealPlan
        fields = ["meal_date", "meal_type", "recipe_name", "protein_grams"]
        widgets = {"meal_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


class JobApplicationForm(BaseStyledModelForm):
    class Meta:
        model = JobApplication
        fields = ["company", "role", "status", "deadline", "notes"]
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


class InventoryItemForm(BaseStyledModelForm):
    class Meta:
        model = InventoryItem
        fields = ["name", "location", "quantity", "reorder_threshold"]


class MessageForm(BaseStyledModelForm):
    class Meta:
        model = Message
        fields = ["recipient", "body"]


class DashboardWidgetForm(BaseStyledModelForm):
    class Meta:
        model = DashboardWidget
        fields = ["visible", "position"]
