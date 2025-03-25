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
    
    # Add policy count for each provider
    for provider in providers:
        provider.policy_count = Policy.objects.filter(provider=provider).count()
        # Get unique categories count
        provider.category_count = Policy.objects.filter(provider=provider).values('category').distinct().count()
    
    policies = Policy.objects.all()
    
    return render(request, 'customer/apply_policy.html', {
        'policies': policies,
        'providers': providers
    })

@login_required
def get_provider_policies(request, provider_id):
    provider = get_object_or_404(User, id=provider_id)
    policies = Policy.objects.filter(provider=provider)
    
    # Convert policies to JSON-serializable format
    policies_data = []
    for policy in policies:
        # Handle different policy model structures
        category_name = ''
        if hasattr(policy, 'category'):
            if isinstance(policy.category, str):
                category_name = policy.category
            elif hasattr(policy.category, 'category_name'):
                category_name = policy.category.category_name
        
        creation_date = ''
        if hasattr(policy, 'creation_date'):
            creation_date = policy.creation_date.isoformat()
        
        policies_data.append({
            'id': policy.id,
            'policy_name': policy.policy_name,
            'category': category_name,
            'sum_assurance': policy.sum_assurance,
            'premium': policy.premium,
            'tenure': policy.tenure,
            'creation_date': creation_date
        })
    
    return JsonResponse({'policies': policies_data})


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
def make_payment_view(request, policy_id):
    """View for customers to make payments for their policies"""
    from .models import PolicyRecord, Payment
    from .forms import PaymentForm
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    
    # Get the policy record and verify it belongs to this customer
    policy_record = get_object_or_404(
        PolicyRecord,
        id=policy_id,  # Changed from policy_id to policy_record_id
        customer=request.user,
        status='APPROVED',  # Only approved policies can be paid
        payment_status__in=['NOT_PAID', 'REJECTED']  # Only unpaid or rejected payments can be paid
    )
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.policy_record = policy_record
            payment.status = 'PENDING'
            
            # Set amount to policy premium if not provided
            if not payment.amount:
                payment.amount = policy_record.policy.premium
                
            # Save the payment
            payment.save()
            
            # Update policy record payment status
            policy_record.payment_status = 'PENDING'
            policy_record.save()
            
            # Create notification for the provider
            from .utils import create_notification
            create_notification(
                recipient=policy_record.policy.provider,
                notification_type='new_payment',
                title='New Payment Received',
                message=f'A new payment of ${payment.amount} has been submitted for {policy_record.policy.policy_name} by {request.user.get_full_name()}.',
                related_link=f'/provider/admin-payment-detail/{payment.id}/'
            )
            
            messages.success(request, 'Your payment has been submitted successfully and is pending approval.')
            return redirect('customer:payment_list')  # Changed to match your URL name
        else:
            messages.error(request, 'There was an error with your payment submission. Please check the form and try again.')
    else:
        form = PaymentForm(initial={'amount': policy_record.policy.premium})
    
    return render(request, 'customer/make_payment.html', {
        'form': form,
        'policy_record': policy_record
    })

@login_required
def payment_list(request):
    """View to display all payments for the customer"""
    from .models import Payment
    
    # Get all payments for this customer
    payments = Payment.objects.filter(policy_record__customer=request.user).order_by('-created_at')
    
    return render(request, 'customer/payment_list.html', {'payments': payments})

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

def policy_categories_view(request):
    categories = Category.objects.all().order_by('category_name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'customer/policy_categories.html', context)

