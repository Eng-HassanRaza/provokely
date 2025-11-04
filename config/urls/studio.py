"""
URL configuration for base domain (provokely.com)
Studio/Hub landing page showing all Provokely products
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static


def studio_home(request):
    """Provokely studio hub landing page"""
    return render(request, 'landing/studio.html')


def privacy(request):
    return render(request, 'landing/privacy.html')


def terms(request):
    return render(request, 'landing/terms.html')


def data_deletion(request):
    return render(request, 'landing/data_deletion.html')


urlpatterns = [
    # Studio hub homepage
    path('', studio_home, name='home'),
    
    # Legal pages
    path('privacy/', privacy, name='privacy'),
    path('terms/', terms, name='terms'),
    path('data-deletion/', data_deletion, name='data_deletion'),
    
    # Django Admin (accessible from base domain)
    path('admin/', admin.site.urls),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

