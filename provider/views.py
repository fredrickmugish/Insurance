from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from . import forms,models
from django.contrib.auth import get_user_model
from customer.models import Question
from django.contrib.auth.forms import UserChangeForm
from customer.models import PolicyRecord  
from customer.forms import QuestionForm
from customer.models import Payment
from .models import Category, Policy
from customer.models import UserProfile
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from customer.models import UserProfile
from django.contrib.auth import update_session_auth_hash

@login_required
def provider_dashboard_view(request):
    dict={
        'total_user': PolicyRecord.objects.filter(policy__provider=request.user).values('customer').distinct().count(),
        'total_policy': Policy.objects.filter(provider=request.user).count(),
        'total_category': Category.objects.filter(policy__provider=request.user).distinct().count(),
        'total_question': Question.objects.filter(customer__customer_policy_records__policy__provider=request.user).count(),
        'total_policy_holder': PolicyRecord.objects.filter(policy__provider=request.user).count(),
        'approved_policy_holder': PolicyRecord.objects.filter(policy__provider=request.user, status='APPROVED').count(),
        'disapproved_policy_holder': PolicyRecord.objects.filter(policy__provider=request.user, status='DISAPPROVED').count(),
        'waiting_policy_holder': PolicyRecord.objects.filter(policy__provider=request.user, status='PENDING').count(),
        'total_payments': Payment.objects.filter(policy_record__policy__provider=request.user).count(),
        'pending_payments': Payment.objects.filter(policy_record__policy__provider=request.user, status='PENDING').count(),
        'confirmed_payments': Payment.objects.filter(policy_record__policy__provider=request.user, status='CONFIRMED').count(),
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
    
    # First, verify the user exists and has policies with this provider
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return redirect('provider:admin-view-customer')
    
    # Get all policy records for this user with the current provider
    from customer.models import PolicyRecord
    policy_records = PolicyRecord.objects.filter(
        customer=user,
        policy__provider=request.user
    )
    
    # Delete only those policy records
    if policy_records.exists():
        policy_records.delete()
    
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

# In provider/views.py
from customer.utils import create_notification

@login_required
def approve_request_view(request, pk):
    policyrecord = PolicyRecord.objects.get(
        policy__provider=request.user,
        id=pk
    )
    policyrecord.status = 'APPROVED'
    policyrecord.save()
    
    # Create notification for the customer
    create_notification(
        recipient=policyrecord.customer,
        notification_type='policy_approval',
        title='Policy Approved',
        message=f'Your application for {policyrecord.policy.policy_name} has been approved.',
        related_link=f'/customer/policy/{policyrecord.id}/'
    )
    
    return redirect('provider:admin-view-policy-holder')
@login_required
def disapprove_request_view(request, pk):
    policyrecord = PolicyRecord.objects.get(
        policy__provider=request.user,
        id=pk
    )
    policyrecord.status = 'DISAPPROVED'
    policyrecord.save()
    
    # Create notification for the customer
    create_notification(
        recipient=policyrecord.customer,
        notification_type='policy_rejection',
        title='Policy Application Rejected',
        message=f'Your application for {policyrecord.policy.policy_name} has been rejected.',
        related_link=f'/customer/policy/{policyrecord.id}/'
    )
    
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
            
            # Create notification for the customer
            create_notification(
                recipient=question.customer,
                notification_type='question_answered',
                title='Your Question Has Been Answered',
                message='Your question has received a response from our team.',
                related_link='/customer/questions/'
            )
            
            return redirect('provider:admin-question')
            
    return render(request, 'provider/update_question.html', {'questionForm': questionForm})



@login_required
def admin_payment_list(request):
    """View to display all payments for the provider"""
    from customer.models import Payment
    payments = Payment.objects.filter(policy_record__policy__provider=request.user)
    return render(request, 'provider/admin_payment_list.html', {'payments': payments})

@login_required
def admin_payment_detail(request, payment_id):
    """View to display payment details and confirm/reject payment"""
    from customer.models import Payment
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    payment = get_object_or_404(Payment, 
                               id=payment_id, 
                               policy_record__policy__provider=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('admin_comment', '')
        
        payment.admin_comment = comment
        
        if action == 'confirm':
            payment.status = 'CONFIRMED'
            
            # Create notification for the customer
            create_notification(
                recipient=payment.policy_record.customer,
                notification_type='payment_received',
                title='Payment Confirmed',
                message=f'Your payment of ${payment.amount} for {payment.policy_record.policy.policy_name} has been confirmed.',
                related_link=f'/customer/payments/'
            )
            
            messages.success(request, 'Payment has been confirmed.')
        
        elif action == 'reject':
            payment.status = 'REJECTED'
            
            # Create notification for the customer
            create_notification(
                recipient=payment.policy_record.customer,
                notification_type='payment_received',
                title='Payment Rejected',
                message=f'Your payment of ${payment.amount} for {payment.policy_record.policy.policy_name} has been rejected. Reason: {comment}',
                related_link=f'/customer/payments/'
            )
            
            messages.warning(request, 'Payment has been rejected.')
        
        payment.save()
        return redirect('provider:admin-payment-list')
    

    return render(request, 'provider/admin_payment_detail.html', {'payment': payment})

@login_required
def provider_profile_view(request):
    # Get or create user profile
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Handle profile image upload
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            profile.profile_image = profile_image
            profile.save()
        
        # Update user information
        user = request.user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('provider:profile')
    
    context = {
        'profile': profile
    }
    return render(request, 'provider/profile.html', context)


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important: update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('provider:change_password')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'provider/change_password.html', {
        'form': form
    })