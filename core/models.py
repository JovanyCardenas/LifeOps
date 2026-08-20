from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=120, blank=True)
    def __str__(self): return self.display_name or self.user.username

class DashboardWidget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=40)
    visible = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ('user','key')
        ordering = ['position','id']

class OwnedModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class ScheduleEvent(OwnedModel):
    CATEGORIES=[('school','School'),('work','Work'),('personal','Personal')]
    title=models.CharField(max_length=180)
    category=models.CharField(max_length=20,choices=CATEGORIES,default='personal')
    starts_at=models.DateTimeField()
    ends_at=models.DateTimeField()
    location=models.CharField(max_length=180,blank=True)
    class Meta: ordering=['starts_at']
    def __str__(self): return self.title

class Requirement(OwnedModel):
    CATEGORIES=[('assignment','Assignment'),('bill','Bill'),('task','Task'),('other','Other')]
    title=models.CharField(max_length=180)
    category=models.CharField(max_length=20,choices=CATEGORIES,default='task')
    due_at=models.DateTimeField(null=True,blank=True)
    completed=models.BooleanField(default=False)
    notes=models.TextField(blank=True)
    class Meta: ordering=['completed','due_at','title']
    def __str__(self): return self.title

class Habit(OwnedModel):
    name=models.CharField(max_length=140)
    target_per_week=models.PositiveSmallIntegerField(default=3)
    current_streak=models.PositiveIntegerField(default=0)
    def __str__(self): return self.name

class BudgetCategory(OwnedModel):
    name=models.CharField(max_length=120)
    monthly_limit=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    current_spend=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    @property
    def remaining(self): return self.monthly_limit-self.current_spend
    def __str__(self): return self.name

class Debt(OwnedModel):
    name=models.CharField(max_length=120)
    balance=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    minimum_payment=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    apr=models.DecimalField(max_digits=6,decimal_places=2,default=0)
    def __str__(self): return self.name

class MealPlan(OwnedModel):
    MEAL_TYPES=[('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner'),('snack','Snack')]
    meal_date=models.DateField()
    meal_type=models.CharField(max_length=20,choices=MEAL_TYPES)
    recipe_name=models.CharField(max_length=180)
    protein_grams=models.PositiveIntegerField(default=0)
    class Meta: ordering=['meal_date','meal_type']
    def __str__(self): return self.recipe_name

class JobApplication(OwnedModel):
    STATUSES=[('saved','Saved'),('applied','Applied'),('interviewing','Interviewing'),('offer','Offer'),('rejected','Rejected')]
    company=models.CharField(max_length=160)
    role=models.CharField(max_length=180)
    status=models.CharField(max_length=20,choices=STATUSES,default='saved')
    deadline=models.DateField(null=True,blank=True)
    notes=models.TextField(blank=True)
    class Meta: ordering=['-updated_at']
    def __str__(self): return f'{self.company} — {self.role}'

class InventoryItem(OwnedModel):
    name=models.CharField(max_length=160)
    location=models.CharField(max_length=160,blank=True)
    quantity=models.PositiveIntegerField(default=1)
    reorder_threshold=models.PositiveIntegerField(default=0)
    @property
    def low_stock(self): return self.quantity <= self.reorder_threshold
    def __str__(self): return self.name

class Message(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_messages')
    recipient=models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_messages')
    body=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    read_at=models.DateTimeField(null=True,blank=True)
    class Meta: ordering=['-created_at']
    def mark_read(self):
        if not self.read_at:
            self.read_at=timezone.now(); self.save(update_fields=['read_at'])
