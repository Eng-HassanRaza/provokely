from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import requests
import hmac
import hashlib
import json
from urllib.parse import urlencode

from shopify_integration.models import ShopifyStore, JudgeReview
from shared.api_responses import success_response, error_response


@login_required
def shopify_install(request):
    """Initiate Shopify OAuth"""
    shop = request.GET.get('shop')
    
    if not shop:
        return error_response('Shop parameter is required', code='VALIDATION_ERROR', status_code=400)
    
    # Ensure shop domain format
    if not shop.endswith('.myshopify.com'):
        shop = f"{shop}.myshopify.com"
    
    # Generate state parameter for security
    state = hmac.new(
        settings.SHOPIFY_API_SECRET.encode(),
        f"{shop}{timezone.now().timestamp()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Store state in session
    request.session['shopify_oauth_state'] = state
    request.session['shopify_shop'] = shop
    
    # Build authorization URL
    params = {
        'client_id': settings.SHOPIFY_API_KEY,
        'scope': settings.SHOPIFY_SCOPES,
        'redirect_uri': settings.SHOPIFY_REDIRECT_URI,
        'state': state,
    }
    
    auth_url = f"https://{shop}/admin/oauth/authorize?{urlencode(params)}"
    
    return redirect(auth_url)


@login_required
def shopify_callback(request):
    """Handle Shopify OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    shop = request.GET.get('shop')
    
    # Verify state parameter
    if state != request.session.get('shopify_oauth_state'):
        return error_response('Invalid state parameter', code='INVALID_STATE', status_code=400)
    
    if not code or not shop:
        return error_response('Missing required parameters', code='VALIDATION_ERROR', status_code=400)
    
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
            return error_response('Failed to get access token', code='TOKEN_ERROR', status_code=400)
        
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
                'logo_url': shop_data.get('logo', {}).get('url'),
                'is_active': True,
            }
        )
        
        # Clear session data
        request.session.pop('shopify_oauth_state', None)
        request.session.pop('shopify_shop', None)
        
        return success_response(
            data={'store_id': store.id, 'store_name': store.store_name},
            message='Shopify store connected successfully'
        )
        
    except requests.RequestException as e:
        return error_response(f'Failed to connect to Shopify: {str(e)}', code='SHOPIFY_ERROR', status_code=502)


@csrf_exempt
@require_POST
def judgeme_webhook(request):
    """
    Receive JudgeMe review webhooks
    POST /api/webhooks/judgeme
    """
    # Verify webhook signature (implement based on JudgeMe documentation)
    # For now, we'll skip verification for development
    
    try:
        payload = json.loads(request.body)
        
        # Extract review data from webhook payload
        review_data = payload.get('review', {})
        product_data = payload.get('product', {})
        
        if not review_data:
            return JsonResponse({'status': 'error', 'message': 'No review data'}, status=400)
        
        # Find the Shopify store (you might need to determine this from the webhook)
        # For now, we'll assume it's passed in the payload
        shop_domain = payload.get('shop_domain')
        if not shop_domain:
            return JsonResponse({'status': 'error', 'message': 'No shop domain'}, status=400)
        
        try:
            store = ShopifyStore.objects.get(shop_domain=shop_domain, is_active=True)
        except ShopifyStore.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Store not found'}, status=404)
        
        # Create JudgeReview record
        review, created = JudgeReview.objects.update_or_create(
            review_id=review_data.get('id'),
            defaults={
                'shopify_store': store,
                'rating': review_data.get('rating', 0),
                'title': review_data.get('title'),
                'body': review_data.get('body', ''),
                'reviewer_name': review_data.get('reviewer', {}).get('name', 'Anonymous'),
                'product_title': product_data.get('title', 'Unknown Product'),
                'product_image_url': product_data.get('image'),
                'processed': False,
            }
        )
        
        # Trigger async task to process review
        from .tasks import process_review_to_instagram
        process_review_to_instagram.delay(review.id)
        
        return JsonResponse({'status': 'received', 'review_id': review.id})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)