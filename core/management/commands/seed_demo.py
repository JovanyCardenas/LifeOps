from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    BudgetCategory,
    DashboardWidget,
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


class Command(BaseCommand):
    help = "Create or refresh the demo account and sample LifeOps data."

    def handle(self, *args, **options):
        demo, _ = User.objects.update_or_create(
            username="demo",
            defaults={
                "email": "demo@example.com",
                "first_name": "Demo",
                "last_name": "User",
            },
        )
        demo.set_password("DemoPass123!")
        demo.save()

        teammate, _ = User.objects.update_or_create(
            username="alex",
            defaults={"email": "alex@example.com", "first_name": "Alex"},
        )
        teammate.set_password("DemoPass123!")
        teammate.save()

        Profile.objects.update_or_create(
            user=demo,
            defaults={"display_name": "Demo User", "role": "Student worker"},
        )

        for model in (
            ScheduleEvent,
            Requirement,
            Habit,
            BudgetCategory,
            Debt,
            MealPlan,
            JobApplication,
            InventoryItem,
        ):
            model.objects.filter(user=demo).delete()
        Message.objects.filter(sender=demo).delete()
        Message.objects.filter(recipient=demo).delete()
        DashboardWidget.objects.filter(user=demo).delete()

        now = timezone.now()
        today = timezone.localdate()

        ScheduleEvent.objects.bulk_create(
            [
                ScheduleEvent(
                    user=demo,
                    title="Data Structures lecture",
                    category=ScheduleEvent.SCHOOL,
                    starts_at=now + timedelta(hours=2),
                    ends_at=now + timedelta(hours=3, minutes=15),
                    location="Engineering Hall",
                ),
                ScheduleEvent(
                    user=demo,
                    title="Part-time shift",
                    category=ScheduleEvent.WORK,
                    starts_at=now + timedelta(days=1, hours=4),
                    ends_at=now + timedelta(days=1, hours=9),
                    location="Campus IT Desk",
                ),
                ScheduleEvent(
                    user=demo,
                    title="Gym: upper body",
                    category=ScheduleEvent.PERSONAL,
                    starts_at=now + timedelta(days=1, hours=11),
                    ends_at=now + timedelta(days=1, hours=12),
                ),
            ]
        )

        Requirement.objects.bulk_create(
            [
                Requirement(
                    user=demo,
                    title="Submit operating systems lab",
                    category=Requirement.ASSIGNMENT,
                    due_at=now + timedelta(days=2),
                ),
                Requirement(
                    user=demo,
                    title="Pay credit card minimum",
                    category=Requirement.BILL,
                    due_at=now + timedelta(days=5),
                ),
                Requirement(
                    user=demo,
                    title="Update resume project section",
                    category=Requirement.TASK,
                    due_at=now + timedelta(days=3),
                ),
            ]
        )

        Habit.objects.bulk_create(
            [
                Habit(user=demo, name="Workout", target_per_week=4, current_streak=8),
                Habit(user=demo, name="Study block", target_per_week=5, current_streak=12),
                Habit(user=demo, name="Meal prep", target_per_week=2, current_streak=3),
            ]
        )

        BudgetCategory.objects.bulk_create(
            [
                BudgetCategory(
                    user=demo,
                    name="Groceries",
                    monthly_limit=Decimal("420.00"),
                    current_spend=Decimal("266.40"),
                ),
                BudgetCategory(
                    user=demo,
                    name="Transportation",
                    monthly_limit=Decimal("180.00"),
                    current_spend=Decimal("74.20"),
                ),
                BudgetCategory(
                    user=demo,
                    name="Subscriptions",
                    monthly_limit=Decimal("65.00"),
                    current_spend=Decimal("42.99"),
                ),
            ]
        )

        Debt.objects.create(
            user=demo,
            name="Student loan",
            balance=Decimal("6400.00"),
            minimum_payment=Decimal("85.00"),
            apr=Decimal("4.80"),
        )

        MealPlan.objects.bulk_create(
            [
                MealPlan(
                    user=demo,
                    meal_date=today,
                    meal_type="Lunch",
                    recipe_name="Chicken rice bowl",
                    protein_grams=42,
                ),
                MealPlan(
                    user=demo,
                    meal_date=today + timedelta(days=1),
                    meal_type="Dinner",
                    recipe_name="Turkey chili",
                    protein_grams=38,
                ),
            ]
        )

        JobApplication.objects.bulk_create(
            [
                JobApplication(
                    user=demo,
                    company="Northstar Labs",
                    role="Software Engineering Intern",
                    status=JobApplication.INTERVIEWING,
                ),
                JobApplication(
                    user=demo,
                    company="Civic Stack",
                    role="Junior Django Developer",
                    status=JobApplication.APPLIED,
                ),
            ]
        )

        InventoryItem.objects.bulk_create(
            [
                InventoryItem(
                    user=demo,
                    name="Protein powder",
                    location="Pantry",
                    quantity=1,
                    reorder_threshold=1,
                ),
                InventoryItem(
                    user=demo,
                    name="Printer paper",
                    location="Desk cabinet",
                    quantity=2,
                    reorder_threshold=1,
                ),
            ]
        )

        Message.objects.create(
            sender=teammate,
            recipient=demo,
            body="Can you send the project outline before our study session?",
        )

        for position, key in enumerate(
            [
                "schedule",
                "requirements",
                "habits",
                "budget",
                "debt",
                "meals",
                "career",
                "inventory",
                "messages",
            ],
            start=1,
        ):
            DashboardWidget.objects.create(user=demo, key=key, position=position)

        self.stdout.write(self.style.SUCCESS("Demo account ready: demo / DemoPass123!"))
