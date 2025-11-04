"""
URL configuration for Provokely project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from core.auth_views import login_view, logout_view, signup_view
from core.api_auth_views import LoginView, MeView
from shopify_integration.views import shopify_install, shopify_callback, judgeme_webhook


# Original Provokely landing page
def provokely_landing(request):
    """Original Provokely landing page - now at root URL"""
    context = {
        'user_count': 247,
        'canonical_url': request.build_absolute_uri('/')
    }
    return render(request, 'landing/index.html', context)


# ReviewFlow landing page
def reviewflow_landing(request):
    """ReviewFlow landing page - distinctive editorial magazine design"""
    context = {
        'canonical_url': request.build_absolute_uri('/reviewflow/')
    }
    return render(request, 'landing/reviewflow.html', context)


def signup_redirect(request):
    return redirect('/admin/')


def newsletter_subscribe(request):
    return JsonResponse({'success': True})


def lead_capture(request):
    return JsonResponse({'success': True})


def contact_submit(request):
    return JsonResponse({'success': True})


def privacy(request):
    return render(request, 'landing/privacy.html')


def terms(request):
    return render(request, 'landing/terms.html')

def data_deletion(request):
    return render(request, 'landing/data_deletion.html')

# API Documentation (uncomment after installing drf-yasg)
# schema_view = get_schema_view(
#     openapi.Info(
#         title="Provokely API",
#         default_version='v1',
#         description="Social Media Sentiment Analysis API for Mobile Apps",
#         terms_of_service="https://www.provokely.com/terms/",
#         contact=openapi.Contact(email="contact@provokely.com"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Landing Pages
    path('', provokely_landing, name='home'),  # Original Provokely landing (restored to root)
    path('reviewflow/', reviewflow_landing, name='reviewflow'),  # ReviewFlow landing page
    
    # Auth & Other Pages
    path('accounts/signup/', signup_view, name='signup'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
    path('lead/capture/', lead_capture, name='lead_capture'),
    path('contact/submit/', contact_submit, name='contact_submit'),
    path('privacy/', privacy, name='privacy'),
    path('terms/', terms, name='terms'),
    path('data-deletion/', data_deletion, name='data_deletion'),
    
    # Dashboard
    path('dashboard/', include('core.dashboard_urls')),
    
    # API v1 endpoints
    path('api/v1/core/', include('core.urls')),
    path('api/v1/instagram/', include('platforms.instagram.urls')),
    
    # Authentication (mobile)
    # Auth endpoints (support both with and without trailing slash)
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

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
