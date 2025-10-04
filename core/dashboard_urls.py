from django.urls import path, include
from core.dashboard_views import dashboard_home, dashboard_accounts, dashboard_settings, dashboard_profile, approve_ai_reply, dashboard_notifications, notifications_poll

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_home, name='home'),
    path('accounts/', dashboard_accounts, name='accounts'),
    path('settings/', dashboard_settings, name='settings'),
    path('notifications/', dashboard_notifications, name='notifications'),
    path('notifications/poll/', notifications_poll, name='notifications_poll'),
    path('profile/', dashboard_profile, name='profile'),
    path('approve-ai-reply/', approve_ai_reply, name='approve_ai_reply'),
    path('instagram/', include('platforms.instagram.dashboard_urls')),
]



