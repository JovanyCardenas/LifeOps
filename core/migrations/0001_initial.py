# Generated for LifeOps initial schema
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Profile',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('display_name',models.CharField(blank=True,max_length=120)),('role',models.CharField(blank=True,max_length=120)),
            ('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='profile',to=settings.AUTH_USER_MODEL)),]),
        migrations.CreateModel(name='DashboardWidget',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('key',models.CharField(max_length=40)),('visible',models.BooleanField(default=True)),('position',models.PositiveIntegerField(default=0)),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),],
            options={'ordering':['position','id'],'unique_together':{('user','key')}}),
        migrations.CreateModel(name='ScheduleEvent',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('title',models.CharField(max_length=180)),('category',models.CharField(choices=[('school','School'),('work','Work'),('personal','Personal')],default='personal',max_length=20)),('starts_at',models.DateTimeField()),('ends_at',models.DateTimeField()),('location',models.CharField(blank=True,max_length=180)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),],options={'ordering':['starts_at']}),
        migrations.CreateModel(name='Requirement',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('title',models.CharField(max_length=180)),('category',models.CharField(choices=[('assignment','Assignment'),('bill','Bill'),('task','Task'),('other','Other')],default='task',max_length=20)),('due_at',models.DateTimeField(blank=True,null=True)),('completed',models.BooleanField(default=False)),('notes',models.TextField(blank=True)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),],options={'ordering':['completed','due_at','title']}),
        migrations.CreateModel(name='Habit',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('name',models.CharField(max_length=140)),('target_per_week',models.PositiveSmallIntegerField(default=3)),('current_streak',models.PositiveIntegerField(default=0)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),]),
        migrations.CreateModel(name='BudgetCategory',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('name',models.CharField(max_length=120)),('monthly_limit',models.DecimalField(decimal_places=2,default=0,max_digits=12)),('current_spend',models.DecimalField(decimal_places=2,default=0,max_digits=12)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),]),
        migrations.CreateModel(name='Debt',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('name',models.CharField(max_length=120)),('balance',models.DecimalField(decimal_places=2,default=0,max_digits=12)),('minimum_payment',models.DecimalField(decimal_places=2,default=0,max_digits=12)),('apr',models.DecimalField(decimal_places=2,default=0,max_digits=6)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),]),
        migrations.CreateModel(name='MealPlan',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('meal_date',models.DateField()),('meal_type',models.CharField(choices=[('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner'),('snack','Snack')],max_length=20)),('recipe_name',models.CharField(max_length=180)),('protein_grams',models.PositiveIntegerField(default=0)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),],options={'ordering':['meal_date','meal_type']}),
        migrations.CreateModel(name='JobApplication',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('company',models.CharField(max_length=160)),('role',models.CharField(max_length=180)),('status',models.CharField(choices=[('saved','Saved'),('applied','Applied'),('interviewing','Interviewing'),('offer','Offer'),('rejected','Rejected')],default='saved',max_length=20)),('deadline',models.DateField(blank=True,null=True)),('notes',models.TextField(blank=True)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),],options={'ordering':['-updated_at']}),
        migrations.CreateModel(name='InventoryItem',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('name',models.CharField(max_length=160)),('location',models.CharField(blank=True,max_length=160)),('quantity',models.PositiveIntegerField(default=1)),('reorder_threshold',models.PositiveIntegerField(default=0)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),]),
        migrations.CreateModel(name='Message',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('body',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),('read_at',models.DateTimeField(blank=True,null=True)),('recipient',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='received_messages',to=settings.AUTH_USER_MODEL)),('sender',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='sent_messages',to=settings.AUTH_USER_MODEL)),],options={'ordering':['-created_at']}),
    ]
