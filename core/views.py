from dataclasses import dataclass

from django.contrib import messages as flash
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    BudgetCategoryForm,
    DashboardWidgetForm,
    DebtForm,
    HabitForm,
    InventoryItemForm,
    JobApplicationForm,
    MealPlanForm,
    MessageForm,
    RequirementForm,
    ScheduleEventForm,
)
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


@dataclass(frozen=True)
class ModuleConfig:
    slug: str
    title: str
    eyebrow: str
    description: str
    model: object
    form_class: object
    add_label: str


MODULES = {
    "schedule": ModuleConfig(
        "schedule",
        "Schedule",
        "Daily planning",
        "Separate school, work, and personal events.",
        ScheduleEvent,
        ScheduleEventForm,
        "Add event",
    ),
    "requirements": ModuleConfig(
        "requirements",
        "Requirements",
        "Assignments and tasks",
        "Track upcoming assignments, bills, and life admin.",
        Requirement,
        RequirementForm,
        "Add requirement",
    ),
    "habits": ModuleConfig(
        "habits",
        "Habits",
        "Consistency",
        "Track weekly targets and current streaks.",
        Habit,
        HabitForm,
        "Add habit",
    ),
    "budget": ModuleConfig(
        "budget",
        "Budget",
        "Personal finance",
        "Manage monthly spending categories.",
        BudgetCategory,
        BudgetCategoryForm,
        "Add category",
    ),
    "debt": ModuleConfig(
        "debt",
        "Debt",
        "Payoff planning",
        "Track balances, payments, and APR.",
        Debt,
        DebtForm,
        "Add debt",
    ),
    "meals": ModuleConfig(
        "meals",
        "Meals",
        "Meal planning",
        "Plan recipes and nutrition for upcoming days.",
        MealPlan,
        MealPlanForm,
        "Add meal",
    ),
    "career": ModuleConfig(
        "career",
        "Career",
        "Job applications",
        "Manage applications, statuses, deadlines, and notes.",
        JobApplication,
        JobApplicationForm,
        "Add application",
    ),
    "inventory": ModuleConfig(
        "inventory",
        "Inventory",
        "Home operations",
        "Track supplies, locations, quantities, and reorder points.",
        InventoryItem,
        InventoryItemForm,
        "Add item",
    ),
}

WIDGET_DEFAULTS = [
    ("schedule", "Schedule"),
    ("requirements", "Requirements"),
    ("habits", "Habits"),
    ("budget", "Budget"),
    ("debt", "Debt"),
    ("meals", "Meals"),
    ("career", "Career"),
    ("inventory", "Inventory"),
    ("messages", "Messages"),
]


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/landing.html")


def demo_login(request):
    user = authenticate(request, username="demo", password="DemoPass123!")
    if user is None:
        user = User.objects.create_user(
            username="demo",
            email="demo@example.com",
            password="DemoPass123!",
            first_name="Demo",
            last_name="User",
        )
    login(request, user)
    return redirect("dashboard")


def ensure_dashboard_widgets(user):
    for position, (key, _label) in enumerate(WIDGET_DEFAULTS, start=1):
        DashboardWidget.objects.get_or_create(
            user=user,
            key=key,
            defaults={"position": position, "visible": True},
        )


def get_module_or_404(slug):
    try:
        return MODULES[slug]
    except KeyError as exc:
        raise Http404("Unknown module") from exc


def object_meta(obj):
    if isinstance(obj, ScheduleEvent):
        return f"{obj.starts_at:%b %d, %I:%M %p} · {obj.get_category_display()}"
    if isinstance(obj, Requirement):
        due = f" · due {obj.due_at:%b %d}" if obj.due_at else ""
        status = "Done" if obj.completed else "Open"
        return f"{obj.get_category_display()} · {status}{due}"
    if isinstance(obj, Habit):
        return f"{obj.current_streak} day streak · {obj.target_per_week}x/week"
    if isinstance(obj, BudgetCategory):
        return f"${obj.current_spend} spent · ${obj.remaining} remaining"
    if isinstance(obj, Debt):
        return f"${obj.balance} balance · ${obj.minimum_payment} minimum · {obj.apr}% APR"
    if isinstance(obj, MealPlan):
        return f"{obj.meal_date:%b %d} · {obj.meal_type} · {obj.protein_grams}g protein"
    if isinstance(obj, JobApplication):
        deadline = f" · deadline {obj.deadline:%b %d}" if obj.deadline else ""
        return f"{obj.company} · {obj.get_status_display()}{deadline}"
    if isinstance(obj, InventoryItem):
        return f"{obj.quantity} in {obj.location or 'storage'} · reorder at {obj.reorder_threshold}"
    return ""


def module_records(config, user):
    return [
        {"object": obj, "title": str(obj), "meta": object_meta(obj)}
        for obj in config.model.objects.filter(user=user)
    ]


@login_required
def dashboard(request):
    ensure_dashboard_widgets(request.user)
    today = timezone.localdate()
    user = request.user
    requirements = Requirement.objects.filter(user=user)
    budgets = BudgetCategory.objects.filter(user=user)
    debts = Debt.objects.filter(user=user)

    widget_data = {
        "schedule": {
            "title": "Schedule",
            "subtitle": "Work, school, personal",
            "section": "schedule",
            "items": module_records(MODULES["schedule"], user)[:5],
        },
        "requirements": {
            "title": "Requirements",
            "subtitle": "Assignments, bills, tasks",
            "section": "requirements",
            "items": module_records(MODULES["requirements"], user)[:6],
        },
        "habits": {
            "title": "Habits",
            "subtitle": "Consistency tracking",
            "section": "habits",
            "items": module_records(MODULES["habits"], user)[:5],
        },
        "budget": {
            "title": "Budget",
            "subtitle": "Monthly categories",
            "section": "budget",
            "items": module_records(MODULES["budget"], user)[:4],
        },
        "debt": {
            "title": "Debt",
            "subtitle": "Balances and payments",
            "section": "debt",
            "items": module_records(MODULES["debt"], user)[:4],
        },
        "meals": {
            "title": "Meals",
            "subtitle": "Recipe planning",
            "section": "meals",
            "items": module_records(MODULES["meals"], user)[:4],
        },
        "career": {
            "title": "Career",
            "subtitle": "Job applications",
            "section": "career",
            "items": module_records(MODULES["career"], user)[:5],
        },
        "inventory": {
            "title": "Inventory",
            "subtitle": "Home and supplies",
            "section": "inventory",
            "items": module_records(MODULES["inventory"], user)[:5],
        },
        "messages": {
            "title": "Messages",
            "subtitle": "Shared planning",
            "section": "messages",
            "items": [
                {"title": f"{msg.sender.username} to {msg.recipient.username}", "meta": msg.body}
                for msg in Message.objects.filter(Q(sender=user) | Q(recipient=user))[:5]
            ],
        },
    }

    widgets = [
        widget_data[widget.key]
        for widget in DashboardWidget.objects.filter(user=user, visible=True)
        if widget.key in widget_data
    ]

    context = {
        "today": today,
        "open_requirements": requirements.filter(completed=False).count(),
        "budget_spend": budgets.aggregate(total=Sum("current_spend"))["total"] or 0,
        "debt_total": debts.aggregate(total=Sum("balance"))["total"] or 0,
        "low_stock_count": InventoryItem.objects.filter(
            user=user,
            quantity__lte=F("reorder_threshold"),
        ).count(),
        "unread_messages": Message.objects.filter(recipient=user, read_at__isnull=True).count(),
        "widgets": widgets,
        "modules": MODULES.values(),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def module_list(request, slug):
    config = get_module_or_404(slug)
    return render(
        request,
        "core/module_list.html",
        {"config": config, "records": module_records(config, request.user)},
    )


@login_required
def module_create(request, slug):
    config = get_module_or_404(slug)
    form = config.form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        flash.success(request, f"{config.title} item added.")
        return redirect("module_list", slug=slug)
    return render(request, "core/item_form.html", {"config": config, "form": form, "mode": "Add"})


@login_required
def module_edit(request, slug, pk):
    config = get_module_or_404(slug)
    instance = get_object_or_404(config.model, pk=pk, user=request.user)
    form = config.form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        flash.success(request, f"{config.title} item updated.")
        return redirect("module_list", slug=slug)
    return render(request, "core/item_form.html", {"config": config, "form": form, "mode": "Edit"})


@login_required
def module_delete(request, slug, pk):
    config = get_module_or_404(slug)
    instance = get_object_or_404(config.model, pk=pk, user=request.user)
    if request.method == "POST":
        instance.delete()
        flash.success(request, f"{config.title} item removed.")
        return redirect("module_list", slug=slug)
    return render(
        request,
        "core/confirm_delete.html",
        {"config": config, "object": instance, "cancel_url": reverse("module_list", args=[slug])},
    )


@login_required
def dashboard_settings(request):
    ensure_dashboard_widgets(request.user)
    widgets = DashboardWidget.objects.filter(user=request.user)
    if request.method == "POST":
        for widget in widgets:
            form = DashboardWidgetForm(request.POST, instance=widget, prefix=widget.key)
            if form.is_valid():
                form.save()
        flash.success(request, "Dashboard layout updated.")
        return redirect("dashboard")

    widget_forms = [
        {
            "widget": widget,
            "label": dict(WIDGET_DEFAULTS).get(widget.key, widget.key.title()),
            "form": DashboardWidgetForm(instance=widget, prefix=widget.key),
        }
        for widget in widgets
    ]
    return render(request, "core/dashboard_settings.html", {"widget_forms": widget_forms})


@login_required
def messages(request):
    user = request.user
    form = MessageForm(request.POST or None)
    form.fields["recipient"].queryset = User.objects.exclude(pk=user.pk)
    if request.method == "POST" and form.is_valid():
        message = form.save(commit=False)
        message.sender = user
        message.save()
        flash.success(request, "Message sent.")
        return redirect("messages")

    message_list = Message.objects.filter(Q(sender=user) | Q(recipient=user)).select_related(
        "sender",
        "recipient",
    )[:20]
    return render(request, "core/messages.html", {"message_list": message_list, "form": form})
