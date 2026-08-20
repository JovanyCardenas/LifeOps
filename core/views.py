from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F, Q, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import (
    BudgetCategory,
    Debt,
    Habit,
    InventoryItem,
    JobApplication,
    MealPlan,
    Message,
    Requirement,
    ScheduleEvent,
)


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


@login_required
def dashboard(request):
    today = timezone.localdate()
    user = request.user
    requirements = Requirement.objects.filter(user=user)
    budgets = BudgetCategory.objects.filter(user=user)
    debts = Debt.objects.filter(user=user)

    context = {
        "today": today,
        "events": ScheduleEvent.objects.filter(user=user, starts_at__date__gte=today)[:5],
        "requirements": requirements[:6],
        "open_requirements": requirements.filter(completed=False).count(),
        "habits": Habit.objects.filter(user=user)[:5],
        "budgets": budgets[:4],
        "budget_spend": budgets.aggregate(total=Sum("current_spend"))["total"] or 0,
        "debt_total": debts.aggregate(total=Sum("balance"))["total"] or 0,
        "meal_plans": MealPlan.objects.filter(user=user, meal_date__gte=today)[:4],
        "job_applications": JobApplication.objects.filter(user=user)[:5],
        "inventory_items": InventoryItem.objects.filter(user=user)[:5],
        "low_stock_count": InventoryItem.objects.filter(
            user=user,
            quantity__lte=F("reorder_threshold"),
        ).count(),
        "unread_messages": Message.objects.filter(recipient=user, read_at__isnull=True).count(),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def messages(request):
    user = request.user
    inbox = Message.objects.filter(Q(sender=user) | Q(recipient=user)).select_related(
        "sender",
        "recipient",
    )[:20]
    return render(request, "core/messages.html", {"messages": inbox})

# Create your views here.
