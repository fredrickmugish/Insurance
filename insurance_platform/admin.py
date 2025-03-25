from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from provider.models import Category, ProviderProfile
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Create an inline for the provider profile
class ProviderProfileInline(admin.StackedInline):
    model = ProviderProfile
    can_delete = False
    verbose_name_plural = 'Provider Information'
    fk_name = 'user'

# Custom form for creating users with provider fields
class CustomUserCreationForm(UserCreationForm):
    is_provider = forms.BooleanField(required=False, label="Register as Provider", 
                                    help_text="Check this if you're registering a provider account")
    company_name = forms.CharField(max_length=100, required=False, 
                                  help_text="Required for providers: Company name as registered")
    business_license = forms.CharField(max_length=50, required=False, 
                                      help_text="Required for providers: Business license number")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean(self):
        cleaned_data = super().clean()
        is_provider = cleaned_data.get('is_provider')
        company_name = cleaned_data.get('company_name')
        business_license = cleaned_data.get('business_license')
        
        if is_provider:
            if not company_name:
                self.add_error('company_name', 'Company name is required for providers')
            if not business_license:
                self.add_error('business_license', 'Business license is required for providers')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # If registering as provider, add to provider group and create profile
            if self.cleaned_data.get('is_provider'):
                provider_group, _ = Group.objects.get_or_create(name='provider')
                user.groups.add(provider_group)
                
                ProviderProfile.objects.create(
                    user=user,
                    company_name=self.cleaned_data.get('company_name', ''),
                    business_license=self.cleaned_data.get('business_license', '')
                )
        
        return user

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_groups', 'get_company_name')
    list_filter = ('groups', 'is_staff', 'is_superuser')
    
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Roles'
    
    def get_company_name(self, obj):
        try:
            return obj.provider_profile.company_name
        except:
            return "-"
    get_company_name.short_description = 'Company'
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Roles', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 
                      'is_provider', 'company_name', 'business_license'),
        }),
    )
    
    add_form = CustomUserCreationForm
    
    inlines = []
    
    def get_inlines(self, request, obj=None):
        if obj and obj.groups.filter(name='provider').exists():
            return [ProviderProfileInline]
        return []

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
