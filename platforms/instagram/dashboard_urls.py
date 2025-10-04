from django.urls import path
from platforms.instagram.dashboard_views import instagram_connect, instagram_disconnect, instagram_settings, instagram_callback, instagram_webhooks, instagram_webhook_mark_processed

app_name = 'instagram'

urlpatterns = [
    path('connect/', instagram_connect, name='connect'),
    path('callback/', instagram_callback, name='callback'),
    path('disconnect/', instagram_disconnect, name='disconnect'),
    path('settings/', instagram_settings, name='settings'),
    path('webhooks/', instagram_webhooks, name='webhooks'),
    path('webhooks/<int:webhook_id>/processed/', instagram_webhook_mark_processed, name='webhook_mark_processed'),
]

