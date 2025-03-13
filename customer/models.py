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
