from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import *

class Command(BaseCommand):
    help='Create or reset realistic LifeOps demo data.'
    def handle(self,*args,**options):
        demo,_=User.objects.get_or_create(username='demo',defaults={'email':'demo@example.com'})
        demo.set_password('DemoPass123!'); demo.save()
        alex,_=User.objects.get_or_create(username='alex',defaults={'email':'alex@example.com'})
        alex.set_password('SamplePass123!'); alex.save()
        Profile.objects.update_or_create(user=demo,defaults={'display_name':'Demo User','role':'Software Engineering Student'})
        Profile.objects.update_or_create(user=alex,defaults={'display_name':'Alex Morgan','role':'Classmate'})
        for model in [ScheduleEvent,Requirement,Habit,BudgetCategory,Debt,MealPlan,JobApplication,InventoryItem]: model.objects.filter(user=demo).delete()
        Message.objects.filter(sender=demo).delete(); Message.objects.filter(recipient=demo).delete()
        DashboardWidget.objects.filter(user=demo).delete()
        now=timezone.now()
        ScheduleEvent.objects.bulk_create([
            ScheduleEvent(user=demo,title='Software Engineering lecture',category='school',starts_at=now+timedelta(hours=3),ends_at=now+timedelta(hours=4,minutes=15),location='Engineering Building'),
            ScheduleEvent(user=demo,title='IT support shift',category='work',starts_at=now+timedelta(days=1,hours=1),ends_at=now+timedelta(days=1,hours=6),location='Sunnyvale Office'),
            ScheduleEvent(user=demo,title='Gym session',category='personal',starts_at=now+timedelta(days=1,hours=8),ends_at=now+timedelta(days=1,hours=9),location='Campus Recreation'),
        ])
        Requirement.objects.bulk_create([
            Requirement(user=demo,title='Submit project milestone',category='assignment',due_at=now+timedelta(days=3),notes='Upload final branch and reflection.'),
            Requirement(user=demo,title='Pay September rent',category='bill',due_at=now+timedelta(days=8)),
            Requirement(user=demo,title='Apply for parking permit',category='task',due_at=now+timedelta(days=2)),
        ])
        Habit.objects.bulk_create([Habit(user=demo,name='Exercise',target_per_week=4,current_streak=3),Habit(user=demo,name='Review coursework',target_per_week=5,current_streak=6),Habit(user=demo,name='Meal prep',target_per_week=2,current_streak=2)])
        BudgetCategory.objects.bulk_create([
            BudgetCategory(user=demo,name='Rent',monthly_limit=Decimal('1200'),current_spend=Decimal('1200')),
            BudgetCategory(user=demo,name='Food',monthly_limit=Decimal('400'),current_spend=Decimal('186.42')),
            BudgetCategory(user=demo,name='Transportation',monthly_limit=Decimal('250'),current_spend=Decimal('93.18')),
        ])
        Debt.objects.bulk_create([Debt(user=demo,name='Credit Card A',balance=Decimal('2380.44'),minimum_payment=Decimal('85'),apr=Decimal('27.49')),Debt(user=demo,name='Student Loan',balance=Decimal('5500'),minimum_payment=Decimal('0'),apr=Decimal('6.53'))])
        MealPlan.objects.bulk_create([MealPlan(user=demo,meal_date=timezone.localdate(),meal_type='lunch',recipe_name='Chicken rice bowl',protein_grams=48),MealPlan(user=demo,meal_date=timezone.localdate()+timedelta(days=1),meal_type='dinner',recipe_name='Protein pasta with chicken',protein_grams=52)])
        JobApplication.objects.bulk_create([JobApplication(user=demo,company='Northstar Dental Group',role='IT Support Technician',status='interviewing',deadline=timezone.localdate()+timedelta(days=4),notes='Prepare troubleshooting examples.'),JobApplication(user=demo,company='Arc Systems',role='Software Engineering Intern',status='applied',deadline=timezone.localdate()+timedelta(days=12))])
        InventoryItem.objects.bulk_create([InventoryItem(user=demo,name='Laundry detergent',location='Bedroom shelf',quantity=1,reorder_threshold=1),InventoryItem(user=demo,name='Protein pasta',location='Kitchen pantry',quantity=4,reorder_threshold=2),InventoryItem(user=demo,name='USB-C cables',location='Desk drawer',quantity=3,reorder_threshold=1)])
        keys=['schedule','requirements','habits','budget','debt','meals','career','inventory','messages']
        DashboardWidget.objects.bulk_create([DashboardWidget(user=demo,key=k,position=i,visible=True) for i,k in enumerate(keys)])
        Message.objects.create(sender=alex,recipient=demo,body='Want to compare notes before the software engineering lecture?')
        Message.objects.create(sender=demo,recipient=alex,body='Absolutely — I’ll send you my outline tonight.')
        self.stdout.write(self.style.SUCCESS('Demo ready: demo / DemoPass123!'))
