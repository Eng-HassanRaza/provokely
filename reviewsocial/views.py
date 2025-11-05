"""
Views for ReviewSocial subdomain (reviewsocial.abandonedrevenue.com)
Shopify app landing page and related views
"""

from django.shortcuts import render
from django.http import JsonResponse


def landing(request):
    """ReviewSocial landing page - Shopify app presentation"""
    context = {
        'canonical_url': request.build_absolute_uri('/')
    }
    return render(request, 'reviewsocial/landing.html', context)


def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    return JsonResponse({'success': True})


def lead_capture(request):
    """Capture leads from landing page"""
    return JsonResponse({'success': True})


def contact_submit(request):
    """Handle contact form submissions"""
    return JsonResponse({'success': True})


def privacy(request):
    """Privacy policy page"""
    return render(request, 'landing/privacy.html')


def terms(request):
    """Terms of service page"""
    return render(request, 'landing/terms.html')


def data_deletion(request):
    """Data deletion policy page (required for Meta apps)"""
    return render(request, 'landing/data_deletion.html')
