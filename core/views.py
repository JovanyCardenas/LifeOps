from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .forms import *
from .models import *

WIDGETS=[
 ('schedule','Schedule'),('requirements','Requirements'),('habits','Habits'),('budget','Budget'),('debt','Debt'),
 ('meals','Meals'),('career','Career'),('inventory','Inventory'),('messages','Messages')
]
MODULES={
 'schedule':(ScheduleEvent,ScheduleEventForm,'Schedule','starts_at'),
 'requirements':(Requirement,RequirementForm,'Requirements','due_at'),
 'habits':(Habit,HabitForm,'Habits','name'),
 'budget':(BudgetCategory,BudgetCategoryForm,'Budget','name'),
 'debt':(Debt,DebtForm,'Debt','name'),
 'meals':(MealPlan,MealPlanForm,'Meals','meal_date'),
 'career':(JobApplication,JobApplicationForm,'Career','company'),
 'inventory':(InventoryItem,InventoryItemForm,'Inventory','name'),
}

def landing(request):
    return render(request,'core/landing.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form=UserCreationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save()
        Profile.objects.get_or_create(user=user,defaults={'display_name':user.username,'role':'LifeOps user'})
        login(request,user)
        return redirect('dashboard')
    return render(request,'registration/signup.html',{'form':form})

@login_required
def profile_settings(request):
    profile,_=Profile.objects.get_or_create(user=request.user,defaults={'display_name':request.user.username})
    if request.method=='POST':
        profile.display_name=request.POST.get('display_name','').strip()[:120]
        profile.role=request.POST.get('role','').strip()[:120]
        request.user.email=request.POST.get('email','').strip()[:254]
        request.user.save(update_fields=['email'])
        profile.save()
        return redirect('profile_settings')
    return render(request,'core/profile_settings.html',{'profile':profile})

def demo_login(request):
    user=get_object_or_404(User,username='demo')
    login(request,user,backend='django.contrib.auth.backends.ModelBackend')
    return redirect('dashboard')

def ensure_widgets(user):
    existing={w.key for w in DashboardWidget.objects.filter(user=user)}
    for pos,(key,_) in enumerate(WIDGETS):
        if key not in existing:
            DashboardWidget.objects.create(user=user,key=key,position=pos,visible=True)

@login_required
def dashboard(request):
    ensure_widgets(request.user)
    widgets=DashboardWidget.objects.filter(user=request.user,visible=True)
    labels=dict(WIDGETS)
    data={
      'schedule': ScheduleEvent.objects.filter(user=request.user).order_by('starts_at')[:5],
      'requirements': Requirement.objects.filter(user=request.user,completed=False).order_by('due_at')[:5],
      'habits': Habit.objects.filter(user=request.user)[:5],
      'budget': BudgetCategory.objects.filter(user=request.user)[:5],
      'debt': Debt.objects.filter(user=request.user).order_by('-balance')[:5],
      'meals': MealPlan.objects.filter(user=request.user).order_by('meal_date')[:5],
      'career': JobApplication.objects.filter(user=request.user)[:5],
      'inventory': InventoryItem.objects.filter(user=request.user).order_by('quantity')[:5],
      'messages': Message.objects.filter(Q(sender=request.user)|Q(recipient=request.user))[:5],
    }
    widget_payload=[{'key':w.key,'label':labels.get(w.key,w.key.title()),'items':data.get(w.key,[])} for w in widgets]
    budget_total=BudgetCategory.objects.filter(user=request.user).aggregate(v=Sum('current_spend'))['v'] or Decimal('0')
    debt_total=Debt.objects.filter(user=request.user).aggregate(v=Sum('balance'))['v'] or Decimal('0')
    context={
      'widgets':widget_payload,
      'open_requirements':Requirement.objects.filter(user=request.user,completed=False).count(),
      'monthly_spend':budget_total,
      'total_debt':debt_total,
      'low_stock':sum(1 for i in InventoryItem.objects.filter(user=request.user) if i.low_stock),
      'unread_messages':Message.objects.filter(recipient=request.user,read_at__isnull=True).count(),
    }
    return render(request,'core/dashboard.html',context)

@login_required
def dashboard_settings(request):
    ensure_widgets(request.user)
    qs=DashboardWidget.objects.filter(user=request.user).order_by('position','id')
    if request.method=='POST':
        ordered=[]
        for w in qs:
            w.visible=request.POST.get(f'visible_{w.id}')=='on'
            try: w.position=int(request.POST.get(f'position_{w.id}',w.position))
            except ValueError: pass
            ordered.append(w)
        DashboardWidget.objects.bulk_update(ordered,['visible','position'])
        return redirect('dashboard')
    return render(request,'core/dashboard_settings.html',{'widgets':qs,'labels':dict(WIDGETS)})

class OwnedQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class OwnedCreateMixin(LoginRequiredMixin):
    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)

class ModuleListView(OwnedQuerysetMixin,ListView):
    template_name='core/module_list.html'
    context_object_name='items'
    def get_context_data(self,**kwargs):
        ctx=super().get_context_data(**kwargs)
        ctx.update(module_key=self.kwargs['module'],module_title=MODULES[self.kwargs['module']][2])
        return ctx
    def dispatch(self,request,*args,**kwargs):
        key=kwargs['module']
        if key not in MODULES: raise Http404
        self.model=MODULES[key][0]
        return super().dispatch(request,*args,**kwargs)

class ModuleCreateView(OwnedCreateMixin,CreateView):
    template_name='core/item_form.html'
    def dispatch(self,request,*args,**kwargs):
        key=kwargs['module']
        if key not in MODULES: raise Http404
        self.model,self.form_class,self.module_title,_=MODULES[key]
        return super().dispatch(request,*args,**kwargs)
    def get_success_url(self): return reverse('module_list',kwargs={'module':self.kwargs['module']})
    def get_context_data(self,**kwargs):
        ctx=super().get_context_data(**kwargs); ctx.update(module_title=self.module_title,action='Add'); return ctx

class ModuleUpdateView(OwnedQuerysetMixin,UpdateView):
    template_name='core/item_form.html'
    def dispatch(self,request,*args,**kwargs):
        key=kwargs['module']
        if key not in MODULES: raise Http404
        self.model,self.form_class,self.module_title,_=MODULES[key]
        return super().dispatch(request,*args,**kwargs)
    def get_success_url(self): return reverse('module_list',kwargs={'module':self.kwargs['module']})
    def get_context_data(self,**kwargs):
        ctx=super().get_context_data(**kwargs); ctx.update(module_title=self.module_title,action='Edit'); return ctx

class ModuleDeleteView(OwnedQuerysetMixin,DeleteView):
    template_name='core/confirm_delete.html'
    def dispatch(self,request,*args,**kwargs):
        key=kwargs['module']
        if key not in MODULES: raise Http404
        self.model,self.form_class,self.module_title,_=MODULES[key]
        return super().dispatch(request,*args,**kwargs)
    def get_success_url(self): return reverse('module_list',kwargs={'module':self.kwargs['module']})
    def get_context_data(self,**kwargs):
        ctx=super().get_context_data(**kwargs); ctx['module_title']=self.module_title; return ctx

@login_required
def messages_page(request):
    if request.method=='POST':
        form=MessageForm(request.POST,current_user=request.user)
        if form.is_valid():
            msg=form.save(commit=False); msg.sender=request.user; msg.save(); return redirect('messages_page')
    else: form=MessageForm(current_user=request.user)
    received=Message.objects.filter(recipient=request.user).select_related('sender')
    sent=Message.objects.filter(sender=request.user).select_related('recipient')
    Message.objects.filter(recipient=request.user,read_at__isnull=True).update(read_at=timezone.now())
    return render(request,'core/messages.html',{'form':form,'received':received,'sent':sent})
