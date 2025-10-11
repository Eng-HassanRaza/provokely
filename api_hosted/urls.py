from django.urls import path
from api_hosted.views import AuthAPIView, AIProxyView

app_name = 'api_hosted'

urlpatterns = [
    path('auth', AuthAPIView.as_view(), name='auth'),
    path('ai', AIProxyView.as_view(), name='ai'),
]

