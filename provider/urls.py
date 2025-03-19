from django.contrib import admin
from django.urls import path
from . import views

app_name = 'provider'

urlpatterns = [
path('provider-dashboard', views.provider_dashboard_view,name='provider-dashboard'),

path('admin-view-customer', views.admin_view_customer_view,name='admin-view-customer'),
path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),
path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),

path('admin-category', views.admin_category_view,name='admin-category'),
path('admin-view-category', views.admin_view_category_view,name='admin-view-category'),
path('admin-update-category', views.admin_update_category_view,name='admin-update-category'),
path('update-category/<int:pk>', views.update_category_view,name='update-category'),
path('admin-add-category', views.admin_add_category_view,name='admin-add-category'),
path('admin-delete-category', views.admin_delete_category_view,name='admin-delete-category'),
path('delete-category/<int:pk>', views.delete_category_view,name='delete-category'),

path('admin-policy', views.admin_policy_view,name='admin-policy'),
path('admin-add-policy', views.admin_add_policy_view,name='admin-add-policy'),
path('admin-view-policy', views.admin_view_policy_view,name='admin-view-policy'),
path('admin-update-policy', views.admin_update_policy_view,name='admin-update-policy'),
path('update-policy/<int:pk>', views.update_policy_view,name='update-policy'),
path('admin-delete-policy', views.admin_delete_policy_view,name='admin-delete-policy'),
path('delete-policy/<int:pk>', views.delete_policy_view,name='delete-policy'),


path('admin-view-policy-holder', views.admin_view_policy_holder_view,name='admin-view-policy-holder'),
path('admin-view-approved-policy-holder', views.admin_view_approved_policy_holder_view,name='admin-view-approved-policy-holder'),
path('admin-view-disapproved-policy-holder', views.admin_view_disapproved_policy_holder_view,name='admin-view-disapproved-policy-holder'),
path('admin-view-waiting-policy-holder', views.admin_view_waiting_policy_holder_view,name='admin-view-waiting-policy-holder'),
path('approve-request/<int:pk>', views.approve_request_view,name='approve-request'),
path('reject-request/<int:pk>', views.disapprove_request_view,name='reject-request'),


path('admin-question', views.admin_question_view,name='admin-question'),
path('update-question/<int:pk>', views.update_question_view,name='update-question'),

path('payments/', views.admin_payment_list, name='admin-payment-list'),
path('payment/<int:payment_id>/', views.admin_payment_detail, name='admin-payment-detail'),

]

