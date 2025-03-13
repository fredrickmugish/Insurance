from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from . import forms,models
from django.contrib.auth import get_user_model
from customer.models import Question
from django.contrib.auth.forms import UserChangeForm
from customer.models import PolicyRecord  
from customer.forms import QuestionForm

@login_required
def provider_dashboard_view(request):
    dict={
        'total_user': models.PolicyRecord.objects.filter(policy__provider=request.user).values('user').distinct().count(),
        'total_policy': models.Policy.objects.filter(provider=request.user).count(),
        'total_category': models.Category.objects.filter(policy__provider=request.user).distinct().count(),
        'total_question': Question.objects.filter(customer__customer_policy_records__policy__provider=request.user).count(),
        'total_policy_holder': models.PolicyRecord.objects.filter(policy__provider=request.user).count(),
        'approved_policy_holder': models.PolicyRecord.objects.filter(policy__provider=request.user, status='Approved').count(),
        'disapproved_policy_holder': models.PolicyRecord.objects.filter(policy__provider=request.user, status='Disapproved').count(),
        'waiting_policy_holder': models.PolicyRecord.objects.filter(policy__provider=request.user, status='Pending').count(),
    }
    return render(request,'provider/dashboard.html', dict)


def admin_category_view(request):
    return render(request,'provider/admin_category.html')

@login_required
def admin_view_customer_view(request):
    User = get_user_model()
    customers = User.objects.filter(
        customer_policy_records__policy__provider=request.user
    ).distinct()
    return render(request, 'provider/admin_view_customer.html', {'customers': customers})
@login_required
def update_customer_view(request, pk):
    User = get_user_model()
    user = User.objects.filter(
        customer_policy_records__policy__provider=request.user,
        id=pk
    ).first()
    
    class CustomUserChangeForm(UserChangeForm):
        class Meta:
            model = User
            fields = ('username', 'first_name', 'last_name', 'email')
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('provider:admin-view-customer')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'provider/update_customer.html', {'form': form})

@login_required
def delete_customer_view(request, pk):
    User = get_user_model()
    user = User.objects.get(
        customer_policy_records__policy__provider=request.user,
        id=pk
    )
    user.delete()
    return redirect('provider:admin-view-customer')

def admin_view_category_view(request):
    categories = models.Category.objects.filter(provider=request.user)
    return render(request, 'provider/admin_view_category.html', {'categories': categories})

def admin_add_category_view(request):
    categoryForm = forms.CategoryForm()
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            category = categoryForm.save(commit=False)
            category.provider = request.user
            category.save()
            return redirect('provider:admin-view-category')
    return render(request, 'provider/admin_add_category.html', {'categoryForm': categoryForm})

def admin_delete_category_view(request):
    categories = models.Category.objects.filter(provider=request.user)
    return render(request, 'provider/admin_delete_category.html', {'categories': categories})

def delete_category_view(request, pk):
    category = models.Category.objects.get(provider=request.user, id=pk)
    category.delete()
    return redirect('provider:admin-delete-category')

def admin_update_category_view(request):
    categories = models.Category.objects.filter(provider=request.user)
    return render(request, 'provider/admin_update_category.html', {'categories': categories})

@login_required
def update_category_view(request, pk):
    category = models.Category.objects.filter(provider=request.user, id=pk).first()
    categoryForm = forms.CategoryForm(instance=category)
    
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST, instance=category)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('provider:admin-update-category')
    return render(request, 'provider/update_category.html', {'categoryForm': categoryForm})

def admin_policy_view(request):
    return render(request, 'provider/admin_policy.html')

@login_required
def admin_add_policy_view(request):
    policyForm = forms.PolicyForm(provider=request.user)
    if request.method == 'POST':
        policyForm = forms.PolicyForm(request.POST, provider=request.user)
        if policyForm.is_valid():
            policy = policyForm.save(commit=False)
            policy.provider = request.user
            policy.save()
            return redirect('provider:admin-view-policy')
    return render(request, 'provider/admin_add_policy.html', {'policyForm': policyForm})

def admin_view_policy_view(request):
    policies = models.Policy.objects.filter(provider=request.user)
    return render(request, 'provider/admin_view_policy.html', {'policies': policies})

def admin_update_policy_view(request):
    policies = models.Policy.objects.filter(provider=request.user)
    return render(request, 'provider/admin_update_policy.html', {'policies': policies})

@login_required
def update_policy_view(request, pk):
    policy = models.Policy.objects.get(id=pk, provider=request.user)
    policyForm = forms.PolicyForm(instance=policy, provider=request.user)
    
    if request.method == 'POST':
        policyForm = forms.PolicyForm(request.POST, instance=policy, provider=request.user)
        if policyForm.is_valid():
            policyForm.save()
            return redirect('provider:admin-view-policy')
    return render(request, 'provider/update_policy.html', {'policyForm': policyForm})

def admin_delete_policy_view(request):
    policies = models.Policy.objects.filter(provider=request.user)
    return render(request, 'provider/admin_delete_policy.html', {'policies': policies})

def delete_policy_view(request, pk):
    policy = models.Policy.objects.get(id=pk, provider=request.user)
    policy.delete()
    return redirect('provider:admin-delete-policy')


@login_required
def admin_view_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.filter(policy__provider=request.user)
    return render(request, 'provider/admin_view_policy_holder.html', {'policyrecords': policyrecords})

@login_required
def admin_view_approved_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.filter(
        policy__provider=request.user,
        status='APPROVED'
    )
    return render(request, 'provider/admin_view_approved_policy_holder.html', {'policyrecords': policyrecords})

@login_required
def admin_view_disapproved_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.filter(
        policy__provider=request.user,
        status='DISAPPROVED'
    )
    return render(request, 'provider/admin_view_disapproved_policy_holder.html', {'policyrecords': policyrecords})

@login_required
def admin_view_waiting_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.filter(
        policy__provider=request.user,
        status='PENDING'
    )
    return render(request, 'provider/admin_view_waiting_policy_holder.html', {'policyrecords': policyrecords})

@login_required
def approve_request_view(request, pk):
    policyrecord = PolicyRecord.objects.get(
        policy__provider=request.user,
        id=pk
    )
    policyrecord.status = 'APPROVED'
    policyrecord.save()
    return redirect('provider:admin-view-policy-holder')

@login_required
def disapprove_request_view(request, pk):
    policyrecord = PolicyRecord.objects.get(
        policy__provider=request.user,
        id=pk
    )
    policyrecord.status = 'DISAPPROVED'
    policyrecord.save()
    return redirect('provider:admin-view-policy-holder')

@login_required
def admin_question_view(request):
    questions = Question.objects.filter(customer__customer_policy_records__policy__provider=request.user)
    return render(request,'provider/admin_question.html',{'questions':questions})

def update_question_view(request, pk):
    question = Question.objects.get(id=pk)
    questionForm = QuestionForm(instance=question)
    
    if request.method == 'POST':
        questionForm = QuestionForm(request.POST, instance=question)
        if questionForm.is_valid():
            admin_comment = request.POST.get('admin_comment')
            question = questionForm.save(commit=False)
            question.admin_comment = admin_comment
            question.save()
            return redirect('provider:admin-question')
    return render(request, 'provider/update_question.html', {'questionForm': questionForm})