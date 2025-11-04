from django.urls import path, include
from core.dashboard_views import dashboard_home

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_home, name='home'),
    path('instagram/', include('platforms.instagram.dashboard_urls')),
    path('shopify/', include('shopify_integration.dashboard_urls')),
]
