from django.db import models
from django.conf import settings
from provider.models import Policy

class PolicyRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DISAPPROVED', 'Disapproved'),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_policy_records')
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='PENDING')
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.policy.policy_name} - {self.get_status_display()}"

class Question(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_questions')
    description = models.CharField(max_length=500)
    admin_comment = models.CharField(max_length=200, default='Nothing')
    asked_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.description


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.email}"

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('policy_approval', 'Policy Approval'),
        ('policy_rejection', 'Policy Rejection'),
        ('payment_due', 'Payment Due'),
        ('payment_received', 'Payment Received'),
        ('question_answered', 'Question Answered'),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    related_link = models.CharField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
    )
    
    PAYMENT_METHODS = (
        ('Bank Transfer', 'Bank Transfer'),
        ('Mobile Money', 'Mobile Money'),
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('Cash', 'Cash'),
    )
    
    policy_record = models.ForeignKey(PolicyRecord, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)  # Made optional since it might not be needed for all payments
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='Bank Transfer')
    receipt_image = models.ImageField(upload_to='payment_receipts/', blank=True, null=True)
    admin_comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment of ${self.amount} for {self.policy_record.policy.policy_name}"
