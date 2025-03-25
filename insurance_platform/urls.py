from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('provider/', include('provider.urls')),
    path('customer/', include('customer.urls')),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('policies/', views.policies_view, name='policies'),
    path('contact/', views.contact_view, name='contact'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)