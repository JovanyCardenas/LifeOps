from django import forms
from django.contrib.auth import get_user_model
from .models import *

DT='%Y-%m-%dT%H:%M'
class DateTimeInput(forms.DateTimeInput): input_type='datetime-local'
class DateInput(forms.DateInput): input_type='date'

class StyledModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class','form-control')

class ScheduleEventForm(StyledModelForm):
    class Meta:
        model=ScheduleEvent; exclude=['user']; widgets={'starts_at':DateTimeInput(format=DT),'ends_at':DateTimeInput(format=DT)}
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw); self.fields['starts_at'].input_formats=[DT]; self.fields['ends_at'].input_formats=[DT]

class RequirementForm(StyledModelForm):
    class Meta:
        model=Requirement; exclude=['user']; widgets={'due_at':DateTimeInput(format=DT)}
    def __init__(self,*a,**kw): super().__init__(*a,**kw); self.fields['due_at'].input_formats=[DT]

class HabitForm(StyledModelForm):
    class Meta: model=Habit; exclude=['user']
class BudgetCategoryForm(StyledModelForm):
    class Meta: model=BudgetCategory; exclude=['user']
class DebtForm(StyledModelForm):
    class Meta: model=Debt; exclude=['user']
class MealPlanForm(StyledModelForm):
    class Meta: model=MealPlan; exclude=['user']; widgets={'meal_date':DateInput()}
class JobApplicationForm(StyledModelForm):
    class Meta: model=JobApplication; exclude=['user']; widgets={'deadline':DateInput()}
class InventoryItemForm(StyledModelForm):
    class Meta: model=InventoryItem; exclude=['user']

class MessageForm(forms.ModelForm):
    class Meta: model=Message; fields=['recipient','body']; widgets={'body':forms.Textarea(attrs={'rows':4,'class':'form-control'})}
    def __init__(self,*a,current_user=None,**kw):
        super().__init__(*a,**kw)
        self.fields['recipient'].queryset=get_user_model().objects.exclude(pk=getattr(current_user,'pk',None)).order_by('username')
        self.fields['recipient'].widget.attrs['class']='form-control'
