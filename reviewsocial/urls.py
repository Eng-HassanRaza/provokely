"""
URL configuration for ReviewSocial subdomain
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.auth_views import login_view, logout_view, signup_view
from core.api_auth_views import LoginView, MeView
from shopify_integration.views import shopify_install, shopify_callback, judgeme_webhook
from reviewsocial import views

app_name = 'reviewsocial'

urlpatterns = [
    # Landing Page
    path('', views.landing, name='landing'),
    
    # Auth Pages
    path('accounts/signup/', signup_view, name='signup'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    
    # Marketing endpoints
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('lead/capture/', views.lead_capture, name='lead_capture'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    
    # Legal pages
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('data-deletion/', views.data_deletion, name='data_deletion'),
    
    # Dashboard
    path('dashboard/', include('core.dashboard_urls')),
    
    # API v1 endpoints
    path('api/v1/core/', include('core.urls')),
    path('api/v1/instagram/', include('platforms.instagram.urls')),
    
    # Authentication (mobile)
    path('api/v1/auth/login', LoginView.as_view(), name='api_login'),
    path('api/v1/auth/login/', LoginView.as_view(), name='api_login_slash'),
    path('api/v1/auth/me', MeView.as_view(), name='api_me'),
    path('api/v1/auth/me/', MeView.as_view(), name='api_me_slash'),
    
    # Hosted API service endpoints
    path('api/', include('api_hosted.urls')),
    
    # Shopify Integration
    path('shopify/install/', shopify_install, name='shopify_install'),
    path('shopify/callback/', shopify_callback, name='shopify_callback'),
    path('api/webhooks/judgeme/', judgeme_webhook, name='judgeme_webhook'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

