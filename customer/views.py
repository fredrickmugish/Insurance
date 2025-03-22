from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from provider.models import Policy, Category
from customer.models import Payment, UserProfile
from .models import PolicyRecord, Question
from . import forms, models
from customer.forms import PaymentForm
from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from customer.utils import create_notification
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import re

@login_required
def customer_dashboard_view(request):
    # Get the current user
    user = request.user
    
    dict = {
        'customer': user,  # Use the user directly instead of Customer model
        'available_policy': Policy.objects.all().count(),
        'applied_policy': PolicyRecord.objects.filter(customer=user).count(),
        'total_category': Category.objects.all().count(),
        'total_question': Question.objects.filter(customer=user).count(),
    }
    
    return render(request, 'customer/dashboard.html', context=dict)

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
    policies = PolicyRecord.objects.filter(customer=request.user).select_related('policy').prefetch_related('payments')
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

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message_text = request.POST.get('message')
        
        # Save to database
        contact_message = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            message=message_text
        )
        contact_message.save()
        
        # Add success message
        messages.success(request, 'Your message has been sent. We will contact you soon!')
        return redirect('contact')
    
    return render(request, 'contact.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification
@login_required
def notifications_list(request):
    """View to display all notifications for the current user"""
    notifications = Notification.objects.filter(recipient=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'customer/notifications_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Redirect to the related link if it exists
    if notification.related_link:
        return redirect(notification.related_link)
    return redirect('customer:notifications_list')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('customer:notifications_list')


@login_required
def payment_list(request):
    """View to display all payments for the customer"""
    payments = Payment.objects.filter(policy_record__customer=request.user)
    return render(request, 'customer/payment_list.html', {'payments': payments})

@login_required
def make_payment_view(request, policy_record_id):
    policy_record = get_object_or_404(PolicyRecord, id=policy_record_id, customer=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.policy_record = policy_record
            payment.customer = request.user
            payment.status = 'PENDING'  # Set initial status to pending
            payment.save()
            
            messages.success(request, 'Your payment has been submitted and is pending confirmation.')
            return redirect('customer:history')
    else:
        form = PaymentForm()
    
    return render(request, 'customer/make_payment.html', {
        'form': form,
        'policy_record': policy_record
    })

@login_required
def profile_view(request):
    # Get the user's profile
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
        return redirect('customer:profile')
    
    context = {
        'profile': profile  # Pass the profile to the template
    }
    return render(request, 'customer/profile.html', context)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if current password is correct
        if not request.user.check_password(current_password):
            messages.error(request, 'Your current password is incorrect.')
            return redirect('customer:change_password')
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('customer:change_password')
        
        # Validate password strength
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('customer:change_password')
        
        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Password must contain at least one uppercase letter.')
            return redirect('customer:change_password')
            
        if not re.search(r'[a-z]', new_password):
            messages.error(request, 'Password must contain at least one lowercase letter.')
            return redirect('customer:change_password')
            
        if not re.search(r'[0-9]', new_password):
            messages.error(request, 'Password must contain at least one number.')
            return redirect('customer:change_password')
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            messages.error(request, 'Password must contain at least one special character.')
            return redirect('customer:change_password')
        
        # Change password
        user = request.user
        user.set_password(new_password)
        user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Your password has been changed successfully!')
        return redirect('customer:customer-dashboard')
    
    return render(request, 'customer/change_password.html')