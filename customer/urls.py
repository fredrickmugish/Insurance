from django.contrib import admin
from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
path('customer-dashboard', views.customer_dashboard_view,name='customer-dashboard'),

path('apply-policy', views.apply_policy_view,name='apply-policy'),
path('apply/<int:pk>', views.apply_view,name='apply'),
path('history', views.history_view,name='history'),

path('ask-question', views.ask_question_view,name='ask-question'),
path('question-history', views.question_history_view,name='question-history'),

]
