from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views
from core.api_settings_views import InstagramSettingsView

app_name = 'core'

router = DefaultRouter()
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'devices', views.DeviceViewSet, basename='device')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('settings/instagram', InstagramSettingsView.as_view(), name='api_instagram_settings'),
]
