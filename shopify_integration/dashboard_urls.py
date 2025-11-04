from django.urls import path
from shopify_integration.dashboard_views import (
    shopify_connect,
    shopify_callback,
    shopify_settings,
    shopify_disconnect,
)

app_name = 'shopify'

urlpatterns = [
    path('connect/', shopify_connect, name='connect'),
    path('callback/', shopify_callback, name='callback'),
    path('settings/', shopify_settings, name='settings'),
    path('disconnect/<int:store_id>/', shopify_disconnect, name='disconnect'),
]




