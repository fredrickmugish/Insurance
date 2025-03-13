from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'creation_date')
    search_fields = ('category_name',)
    list_filter = ('creation_date',)
    
admin.site.register(Category, CategoryAdmin)
