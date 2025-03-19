from django.db import models
from django.conf import settings

class Category(models.Model):
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100)
    creation_date = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.category_name

class Policy(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_policies')
    policy_name = models.CharField(max_length=200)
    sum_assurance = models.PositiveIntegerField()
    premium = models.PositiveIntegerField()
    tenure = models.PositiveIntegerField()
    creation_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "Policy"
        verbose_name_plural = "Policies"
    
    def __str__(self):
        return f"{self.policy_name} by {self.provider.username}"