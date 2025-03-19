from django.contrib import admin
from .models import Category, Policy
from customer.models import PolicyRecord, Question, ContactMessage  # Import the models from customer app

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'creation_date')
    search_fields = ('category_name',)
    list_filter = ('creation_date',)
    

class PolicyAdmin(admin.ModelAdmin):
    list_display = ('provider', 'policy_name', 'category', 'sum_assurance', 'premium', 'tenure', 'creation_date')
    search_fields = ('policy_name',)
    list_filter = ('category', 'provider', 'creation_date')
    

class PolicyRecordAdmin(admin.ModelAdmin):
    list_display = ('customer', 'policy', 'status', 'creation_date')
    search_fields = ('customer__username', 'policy__policy_name')
    list_filter = ('status', 'creation_date', 'policy__provider')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('description', 'customer', 'admin_comment', 'asked_date')
    search_fields = ('description', 'customer__username')
    list_filter = ('asked_date',)

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'message', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(PolicyRecord, PolicyRecordAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)