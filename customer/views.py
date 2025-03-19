from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from provider.models import Policy
from customer.models import Payment
from .models import PolicyRecord, Question
from . import forms, models
from customer.forms import PaymentForm
from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from customer.utils import create_notification

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
def make_payment(request, policy_id):
    """View to make a payment for a policy"""
    policy_record = get_object_or_404(PolicyRecord, id=policy_id, customer=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.policy_record = policy_record
            payment.status = 'PENDING'
            payment.save()
            
            # Create notification for the provider
            create_notification(
                recipient=policy_record.policy.provider,
                notification_type='payment_due',
                title='New Payment Submission',
                message=f'A payment of ${payment.amount} has been submitted for {policy_record.policy.policy_name} by {request.user.get_full_name()}.',
                related_link=f'/provider/payments/{payment.id}/'
            )
            
            messages.success(request, 'Payment submitted successfully. It will be reviewed by the provider.')
            return redirect('customer:payment_list')
    else:
        # Pre-fill with the policy premium amount
        form = PaymentForm(initial={'amount': policy_record.policy.premium})
    
    return render(request, 'customer/make_payment.html', {
        'form': form,
        'policy_record': policy_record
    })