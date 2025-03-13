from django import forms
from django.contrib.auth.models import User
from . import models
from django.contrib.auth import get_user_model

class CategoryForm(forms.ModelForm):
    class Meta:
        model=models.Category
        fields=['category_name']

class PolicyForm(forms.ModelForm):
    def __init__(self, *args, provider=None, **kwargs):
        super().__init__(*args, **kwargs)
        if provider:
            self.fields['category'].queryset = models.Category.objects.filter(provider=provider)

    class Meta:
        model = models.Policy
        fields = ['category', 'policy_name', 'sum_assurance', 'premium', 'tenure']
