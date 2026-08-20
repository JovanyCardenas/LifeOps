from django.conf import settings
from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.display_name or self.user.get_username()


class DashboardWidget(TimeStampedModel):
    SCHEDULE = "schedule"
    REQUIREMENTS = "requirements"
    HABITS = "habits"
    BUDGET = "budget"
    DEBT = "debt"
    MEALS = "meals"
    CAREER = "career"
    INVENTORY = "inventory"
    MESSAGES = "messages"
    WIDGET_CHOICES = [
        (SCHEDULE, "Schedule"),
        (REQUIREMENTS, "Requirements"),
        (HABITS, "Habits"),
        (BUDGET, "Budget"),
        (DEBT, "Debt"),
        (MEALS, "Meals"),
        (CAREER, "Career"),
        (INVENTORY, "Inventory"),
        (MESSAGES, "Messages"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=32, choices=WIDGET_CHOICES)
    visible = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "key"]
        unique_together = ("user", "key")

    def __str__(self):
        return f"{self.user} · {self.get_key_display()}"


class ScheduleEvent(TimeStampedModel):
    SCHOOL = "school"
    WORK = "work"
    PERSONAL = "personal"
    CATEGORY_CHOICES = [
        (SCHOOL, "School"),
        (WORK, "Work"),
        (PERSONAL, "Personal"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=PERSONAL)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title


class Requirement(TimeStampedModel):
    ASSIGNMENT = "assignment"
    BILL = "bill"
    TASK = "task"
    OTHER = "other"
    CATEGORY_CHOICES = [
        (ASSIGNMENT, "Assignment"),
        (BILL, "Bill"),
        (TASK, "Task"),
        (OTHER, "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES, default=TASK)
    due_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["completed", "due_at", "title"]

    def __str__(self):
        return self.title


class Habit(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    target_per_week = models.PositiveSmallIntegerField(default=5)
    current_streak = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class BudgetCategory(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "budget categories"

    @property
    def remaining(self):
        return self.monthly_limit - self.current_spend

    def __str__(self):
        return self.name


class Debt(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_payment = models.DecimalField(max_digits=10, decimal_places=2)
    apr = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class MealPlan(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meal_date = models.DateField()
    meal_type = models.CharField(max_length=40)
    recipe_name = models.CharField(max_length=160)
    protein_grams = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["meal_date", "meal_type"]

    def __str__(self):
        return f"{self.recipe_name} ({self.meal_type})"


class JobApplication(TimeStampedModel):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    STATUS_CHOICES = [
        (SAVED, "Saved"),
        (APPLIED, "Applied"),
        (INTERVIEWING, "Interviewing"),
        (OFFER, "Offer"),
        (REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.CharField(max_length=140)
    role = models.CharField(max_length=140)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=SAVED)
    deadline = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["company", "role"]

    def __str__(self):
        return f"{self.role} at {self.company}"


class InventoryItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=140)
    location = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    reorder_threshold = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Message(TimeStampedModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    body = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("messages")

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"

# Create your models here.
