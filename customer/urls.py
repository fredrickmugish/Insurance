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

path('contact/', views.contact_view, name='contact'),
path('notifications/', views.notifications_list, name='notifications_list'),
path('notifications/', views.notifications_list, name='notifications_list'),
path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),

path('payments/', views.payment_list, name='payment_list'),
path('make-payment/<int:policy_id>/', views.make_payment_view, name='make_payment'),

path('profile/', views.profile_view, name='profile'),
path('change-password/', views.change_password_view, name='change_password'),
path('policy-categories/', views.policy_categories_view, name='policy-categories'),

path('get-provider-policies/<int:provider_id>/', views.get_provider_policies, name='get-provider-policies'),

]
