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
# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi


# Landing page views
def landing(request):
    context = {
        'user_count': 247,
        'canonical_url': request.build_absolute_uri('/')
    }
    return render(request, 'landing/index.html', context)


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
    
    # Landing Page
    path('', landing, name='home'),
    path('accounts/signup/', signup_view, name='signup'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
    path('lead/capture/', lead_capture, name='lead_capture'),
    path('contact/submit/', contact_submit, name='contact_submit'),
    path('privacy/', privacy, name='privacy'),
    
    # API Documentation (uncomment after installing drf-yasg)
    # path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
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
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
