from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import UserSettings, InstagramPost
from platforms.instagram.models import InstagramAccount
from shopify_integration.models import ShopifyStore


@login_required
def dashboard_home(request):
    """Main dashboard home page"""
    # Get user's Instagram connection status
    try:
        instagram_account = InstagramAccount.objects.get(user=request.user)
        instagram_connected = True
        instagram_username = instagram_account.username
    except InstagramAccount.DoesNotExist:
        instagram_connected = False
        instagram_username = None
        instagram_account = None
    
    # Get user's Shopify stores
    shopify_stores = ShopifyStore.objects.filter(user=request.user, is_active=True)
    shopify_connected = shopify_stores.exists()
    
    # Get recent Instagram posts
    recent_posts = InstagramPost.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get user settings
    try:
        user_settings = UserSettings.objects.get(user=request.user)
    except UserSettings.DoesNotExist:
        user_settings = UserSettings.objects.create(user=request.user)

    context = {
        'instagram_connected': instagram_connected,
        'instagram_username': instagram_username,
        'shopify_connected': shopify_connected,
        'shopify_stores': shopify_stores,
        'recent_posts': recent_posts,
        'user_settings': user_settings,
    }
    
    return render(request, 'dashboard/home.html', context)