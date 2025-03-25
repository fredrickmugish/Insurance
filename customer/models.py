from django.db import models
from django.conf import settings
from provider.models import Policy
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class PolicyRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DISAPPROVED', 'Disapproved'),
    ]
    
    # Add payment status choices
    PAYMENT_STATUS_CHOICES = [
        ('NOT_PAID', 'Not Paid'),
        ('PENDING', 'Payment Pending'),
        ('PAID', 'Paid'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_policy_records')
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='PENDING')
    # Add payment status field
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='NOT_PAID')
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

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('policy_approval', 'Policy Approval'),
        ('policy_rejection', 'Policy Rejection'),
        ('payment_due', 'Payment Due'),
        ('payment_received', 'Payment Received'),
        ('payment_rejected', 'Payment Rejected'),  # Add this type
        ('question_answered', 'Question Answered'),
        ('new_payment', 'New Payment'),  # Add this type
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
        ('CRDB Bank', 'CRDB Bank'),
        ('NMB Bank', 'NMB Bank'),
        ('NBC Bank', 'NBC Bank'),
        ('M-Pesa', 'M-Pesa'),
        ('Tigo Pesa', 'Tigo Pesa'),
        ('Airtel Money', 'Airtel Money'),
        ('Halo Pesa', 'Halo Pesa'),
        ('Azam Pesa', 'Azam Pesa'),
    )
    
    policy_record = models.ForeignKey(PolicyRecord, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()  # Changed from auto_now_add to allow user to specify date
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='CRDB Bank')
    receipt_image = models.ImageField(upload_to='payment_receipts/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    admin_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this to track when payment was submitted
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='processed_payments')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment of ${self.amount} for {self.policy_record.policy.policy_name}"

# Modified UserProfile model with new fields
class UserProfile(models.Model):
    IDENTITY_TYPE_CHOICES = [
        ('nida', 'NIDA Number'),
        ('voter', 'Voter ID Number'),
        ('driving', 'Driving License Number'),
        ('passport', 'Passport Number')
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    # Add new fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    identity_type = models.CharField(max_length=20, choices=IDENTITY_TYPE_CHOICES, blank=True, null=True)
    identity_number = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

# Create UserProfile automatically when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
