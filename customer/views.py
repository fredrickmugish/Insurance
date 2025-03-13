from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from provider.models import Policy
from .models import PolicyRecord, Question
from . import forms, models
from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group


@login_required
def customer_dashboard_view(request):
    dict={
        'customer':models.Customer.objects.get(user_id=request.user.id),
        'available_policy':Policy.objects.all().count(),
        'applied_policy':PolicyRecord.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_category':models.Category.objects.all().count(),
        'total_question':Question.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
    }
    return render(request,'customer/dashboard.html',context=dict)

@login_required
def apply_policy_view(request):
    provider_group = Group.objects.get(name='provider')
    providers = User.objects.filter(groups=provider_group)
    policies = Policy.objects.all()
    
    return render(request, 'customer/apply_policy.html', {
        'policies': policies,
        'providers': providers
    })


@login_required
def apply_view(request, pk):
    policy = Policy.objects.get(id=pk)
    policyrecord = PolicyRecord()
    policyrecord.policy = policy
    policyrecord.customer = request.user
    policyrecord.save()
    return redirect('customer:history')

@login_required
def history_view(request):
    policies = PolicyRecord.objects.filter(customer=request.user)
    return render(request, 'customer/history.html', {'policies': policies})


@login_required
def ask_question_view(request):
    questionForm = forms.QuestionForm()
    if request.method == 'POST':
        questionForm = forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            question.customer = request.user
            question.save()
            return redirect('customer:question-history')
    return render(request, 'customer/ask_question.html', {'questionForm': questionForm})

@login_required
def question_history_view(request):
    questions = Question.objects.filter(customer=request.user)
    return render(request, 'customer/question_history.html', {'questions': questions})
