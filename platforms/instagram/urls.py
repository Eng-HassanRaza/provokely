from django.urls import path, include
from rest_framework.routers import DefaultRouter
from platforms.instagram import views

app_name = 'instagram'

router = DefaultRouter()
router.register(r'accounts', views.InstagramAccountViewSet, basename='account')
router.register(r'webhooks', views.InstagramWebhookViewSet, basename='webhook')

urlpatterns = [
    path('', include(router.urls)),
    path('mobile/callback/', views.mobile_oauth_callback, name='mobile_oauth_callback'),
]
