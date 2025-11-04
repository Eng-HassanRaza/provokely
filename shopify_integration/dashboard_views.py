from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
import requests
import hmac
import hashlib
from urllib.parse import urlencode

from shopify_integration.models import ShopifyStore


@login_required
def shopify_connect(request):
    """Connect Shopify store - show form or initiate OAuth"""
    if request.method == 'POST':
        shop = request.POST.get('shop', '').strip()
        
        if not shop:
            messages.error(request, 'Please enter your Shopify store domain')
            return render(request, 'dashboard/shopify/connect.html')
        
        # Ensure shop domain format
        if not shop.endswith('.myshopify.com'):
            shop = f"{shop}.myshopify.com"
        
        # Remove the shop part if user entered full domain
        shop_domain = shop.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Generate state parameter for security
        state = hmac.new(
            settings.SHOPIFY_API_SECRET.encode(),
            f"{shop_domain}{timezone.now().timestamp()}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Store state in session
        request.session['shopify_oauth_state'] = state
        request.session['shopify_shop'] = shop_domain
        
        # Build authorization URL
        params = {
            'client_id': settings.SHOPIFY_API_KEY,
            'scope': settings.SHOPIFY_SCOPES,
            'redirect_uri': settings.SHOPIFY_REDIRECT_URI,
            'state': state,
        }
        
        auth_url = f"https://{shop_domain}/admin/oauth/authorize?{urlencode(params)}"
        
        return redirect(auth_url)
    
    # GET request - show connect form
    return render(request, 'dashboard/shopify/connect.html')


@login_required
def shopify_callback(request):
    """Handle Shopify OAuth callback and redirect to dashboard"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    shop = request.GET.get('shop')
    
    # Verify state parameter
    if state != request.session.get('shopify_oauth_state'):
        messages.error(request, 'Invalid authentication state. Please try connecting again.')
        return redirect('dashboard:home')
    
    if not code or not shop:
        messages.error(request, 'Missing required parameters from Shopify')
        return redirect('dashboard:home')
    
    # Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"
    token_data = {
        'client_id': settings.SHOPIFY_API_KEY,
        'client_secret': settings.SHOPIFY_API_SECRET,
        'code': code,
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=30)
        response.raise_for_status()
        token_response = response.json()
        
        access_token = token_response.get('access_token')
        if not access_token:
            messages.error(request, 'Failed to get access token from Shopify')
            return redirect('dashboard:home')
        
        # Get shop information
        shop_url = f"https://{shop}/admin/api/2023-10/shop.json"
        headers = {'X-Shopify-Access-Token': access_token}
        
        shop_response = requests.get(shop_url, headers=headers, timeout=30)
        shop_response.raise_for_status()
        shop_data = shop_response.json()['shop']
        
        # Create or update ShopifyStore
        store, created = ShopifyStore.objects.update_or_create(
            shop_domain=shop,
            defaults={
                'user': request.user,
                'access_token': access_token,
                'store_name': shop_data.get('name', shop),
                'logo_url': shop_data.get('logo', {}).get('url') if shop_data.get('logo') else None,
                'is_active': True,
            }
        )
        
        # Clear session data
        request.session.pop('shopify_oauth_state', None)
        request.session.pop('shopify_shop', None)
        
        if created:
            messages.success(request, f'Successfully connected to {store.store_name}!')
        else:
            messages.success(request, f'Updated connection to {store.store_name}!')
        
        return redirect('dashboard:home')
        
    except requests.RequestException as e:
        messages.error(request, f'Failed to connect to Shopify: {str(e)}')
        return redirect('dashboard:home')


@login_required
def shopify_settings(request):
    """View and manage connected Shopify stores"""
    stores = ShopifyStore.objects.filter(user=request.user, is_active=True).order_by('-installed_at')
    
    context = {
        'stores': stores,
    }
    
    return render(request, 'dashboard/shopify/settings.html', context)


@login_required
def shopify_disconnect(request, store_id):
    """Disconnect a Shopify store"""
    store = get_object_or_404(ShopifyStore, id=store_id, user=request.user)
    
    if request.method == 'POST':
        store_name = store.store_name
        store.is_active = False
        store.save()
        
        messages.success(request, f'Disconnected from {store_name}')
        return redirect('dashboard:shopify:settings')
    
    # GET request - show confirmation
    context = {
        'store': store,
    }
    return render(request, 'dashboard/shopify/disconnect.html', context)

