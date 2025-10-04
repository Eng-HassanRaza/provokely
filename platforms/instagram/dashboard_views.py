from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.utils.crypto import get_random_string
from platforms.instagram.models import InstagramAccount
from platforms.instagram.models import InstagramWebhook
from platforms.instagram.serializers import InstagramAccountSerializer
from platforms.instagram.services import InstagramService
from shared.exceptions import PlatformAPIError
from core.models import UserSettings


@login_required
def instagram_connect(request):
    """Instagram connection page - redirects to OAuth"""
    # Check if already connected
    try:
        InstagramAccount.objects.get(user=request.user)
        messages.info(request, 'Instagram account is already connected.')
        return redirect('dashboard:home')
    except InstagramAccount.DoesNotExist:
        pass
    
    # Check if Instagram credentials are configured
    missing_keys = []
    if not getattr(settings, 'INSTAGRAM_CLIENT_ID', None):
        missing_keys.append('INSTAGRAM_CLIENT_ID')
    if not getattr(settings, 'INSTAGRAM_CLIENT_SECRET', None):
        missing_keys.append('INSTAGRAM_CLIENT_SECRET')
    if not getattr(settings, 'INSTAGRAM_REDIRECT_URI', None):
        missing_keys.append('INSTAGRAM_REDIRECT_URI')
    
    if missing_keys:
        if settings.DEBUG:
            print(f"Instagram config missing: {missing_keys}")
        messages.error(request, 'Instagram integration is not configured. Please contact support.')
        return redirect('dashboard:home')
    
    try:
        # Generate OAuth authorization URL
        instagram_service = InstagramService()
        
        # Generate secure random state parameter
        state = get_random_string(32)
        fixed_redirect_uri = settings.INSTAGRAM_REDIRECT_URI
        auth_url = instagram_service.get_authorization_url(state=state, redirect_uri=fixed_redirect_uri)
        
        # No verbose logging in production
        
        # Store state and user ID in session for security and session recovery
        request.session['instagram_oauth_state'] = state
        request.session['instagram_oauth_user_id'] = request.user.id
        request.session.modified = True  # Mark session as modified
        request.session.save()  # Force session save
        
        return redirect(auth_url)
    except Exception as e:
        messages.error(request, f'Failed to start Instagram connection: {str(e)}')
        return redirect('dashboard:home')


def instagram_callback(request):
    """Handle Instagram OAuth callback"""
    # Check if user is authenticated, if not try to recover from session
    if not request.user.is_authenticated:
        # Try to get user ID from session
        user_id = request.session.get('instagram_oauth_user_id')
        if user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                # Log the user back in
                from django.contrib.auth import login
                login(request, user)
                if settings.DEBUG:
                    print(f"Session recovered for user: {user.username}")
            except User.DoesNotExist:
                messages.error(request, 'Session expired. Please log in again.')
                return redirect('dashboard:home')
        else:
            messages.error(request, 'Please log in first, then try connecting Instagram.')
            return redirect('dashboard:home')
    
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_reason = request.GET.get('error_reason')
    error_description = request.GET.get('error_description')
    
    # Handle Facebook OAuth errors
    if error:
        error_msg = f'Instagram authorization failed: {error}'
        if error_reason:
            error_msg += f' - {error_reason}'
        if error_description:
            error_msg += f' - {error_description}'
        
        if settings.DEBUG:
            print(f"OAuth Error: {error_msg}")
            print(f"Error Reason: {error_reason}")
            print(f"Error Description: {error_description}")
        
        # Provide user-friendly error messages
        if error == 'access_denied' or error_reason == 'user_denied':
            messages.warning(request, 'Instagram connection was cancelled. Please try again when ready.')
        else:
            messages.error(request, error_msg)
        
        return redirect('dashboard:home')
    
    if not code:
        messages.error(request, 'No authorization code received from Instagram.')
        return redirect('dashboard:home')
    
    # Verify state parameter
    stored_state = request.session.get('instagram_oauth_state')
    
    # Minimal debug only when needed
    
    if not stored_state:
        messages.error(request, 'Session expired. Please try connecting again.')
        return redirect('dashboard:home')
    
    if state != stored_state:
        messages.error(request, 'Invalid state parameter. Please try again.')
        return redirect('dashboard:home')
    
    try:
        instagram_service = InstagramService()
        
        # No verbose callback logs
        
        # Authenticate with Instagram
        try:
            fixed_redirect_uri = settings.INSTAGRAM_REDIRECT_URI
            auth_data = instagram_service.authenticate({'code': code, 'redirect_uri': fixed_redirect_uri})
            
            
        except PlatformAPIError as api_error:
            error_message = str(api_error)
            
            
            
            # Provide helpful error messages based on common issues
            if 'No Instagram business account found' in error_message:
                messages.error(request, 'No Instagram Business account found. Please ensure: 1) Your Instagram is a Business/Creator account, 2) It is linked to a Facebook Page, 3) You have Admin access to that Page.')
            elif 'not accessible' in error_message or 'permissions' in error_message.lower():
                messages.error(request, 'Cannot access Instagram account. Make sure you granted all required permissions and your Facebook App is properly configured.')
            else:
                messages.error(request, f'Failed to connect Instagram: {error_message}')
            
            return redirect('dashboard:home')
        
        
        
        # Create or update Instagram account
        account, created = InstagramAccount.objects.update_or_create(
            user=request.user,
            instagram_user_id=auth_data['user_id'],
            defaults={
                'username': auth_data['username'],
                'access_token': auth_data['access_token'],
                'expires_in': auth_data.get('expires_in'),
                'account_type': auth_data.get('account_type', 'PERSONAL'),
                'media_count': auth_data.get('media_count', 0),
                'is_active': True,
            }
        )
        
        if created:
            messages.success(request, f'Successfully connected to @{auth_data["username"]}!')
        else:
            messages.success(request, f'Instagram account @{auth_data["username"]} updated!')
        
        # Clean up session
        if 'instagram_oauth_state' in request.session:
            del request.session['instagram_oauth_state']
        if 'instagram_oauth_user_id' in request.session:
            del request.session['instagram_oauth_user_id']
        request.session.save()
        
        return redirect('dashboard:home')
        
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return redirect('dashboard:home')


@login_required
def instagram_disconnect(request):
    """Disconnect Instagram account"""
    if request.method == 'POST':
        try:
            account = InstagramAccount.objects.get(user=request.user)
            username = account.username
            account.delete()
            messages.success(request, f'Successfully disconnected @{username}')
        except InstagramAccount.DoesNotExist:
            messages.error(request, 'No Instagram account connected.')
    
    return redirect('dashboard:home')


@login_required
def instagram_settings(request):
    """Instagram account settings"""
    try:
        account = InstagramAccount.objects.get(user=request.user)
    except InstagramAccount.DoesNotExist:
        messages.error(request, 'No Instagram account connected.')
        return redirect('dashboard:home')
    
    # Load or create user settings (per-user, platform-agnostic)
    try:
        user_settings = UserSettings.objects.get(user=request.user)
    except UserSettings.DoesNotExist:
        user_settings = UserSettings.objects.create(user=request.user)

    if request.method == 'POST':
        # Update account active flag
        account.is_active = request.POST.get('is_active') == 'on'
        account.save()

        # Auto-reply master toggle
        auto_enabled = request.POST.get('auto_comment_enabled') == 'on'
        user_settings.auto_comment_enabled = auto_enabled
        # Per-sentiment toggles
        user_settings.auto_respond_to_positive = request.POST.get('auto_respond_to_positive') == 'on'
        user_settings.auto_respond_to_negative = request.POST.get('auto_respond_to_negative') == 'on'
        user_settings.auto_respond_to_hate = request.POST.get('auto_respond_to_hate') == 'on'
        # Approval settings only applicable if auto-reply is enabled AND that sentiment auto-reply is enabled
        if auto_enabled and user_settings.auto_respond_to_negative:
            user_settings.require_approval_for_negative = request.POST.get('require_approval_for_negative') == 'on'
        else:
            user_settings.require_approval_for_negative = False
        if auto_enabled and user_settings.auto_respond_to_hate:
            user_settings.require_approval_for_hate = request.POST.get('require_approval_for_hate') == 'on'
        else:
            user_settings.require_approval_for_hate = False
        # Notification prefs
        user_settings.notify_on_positive = request.POST.get('notify_on_positive') == 'on'
        user_settings.notify_on_negative = request.POST.get('notify_on_negative') == 'on'
        user_settings.notify_on_hate = request.POST.get('notify_on_hate') == 'on'
        user_settings.notify_on_neutral = request.POST.get('notify_on_neutral') == 'on'
        user_settings.notify_on_purchase_intent = request.POST.get('notify_on_purchase_intent') == 'on'
        user_settings.notify_on_question = request.POST.get('notify_on_question') == 'on'
        user_settings.save()
        
        messages.success(request, 'Instagram auto-reply settings updated!')
        return redirect('dashboard:instagram:settings')
    
    context = {
        'account': account,
        'user_settings': user_settings,
    }
    
    return render(request, 'dashboard/instagram/settings.html', context)


@login_required
def instagram_webhooks(request):
    """List recent Instagram webhooks for the current user's account"""
    try:
        account = InstagramAccount.objects.get(user=request.user)
    except InstagramAccount.DoesNotExist:
        messages.error(request, 'No Instagram account connected.')
        return redirect('dashboard:home')
    webhooks = account.webhooks.all()[:20]
    context = {
        'account': account,
        'webhooks': webhooks,
    }
    return render(request, 'dashboard/instagram/webhooks.html', context)


@login_required
def instagram_webhook_mark_processed(request, webhook_id: int):
    """Mark a webhook event as processed and return to list"""
    try:
        webhook = InstagramWebhook.objects.get(id=webhook_id, account__user=request.user)
        webhook.processed = True
        webhook.save()
        messages.success(request, 'Webhook marked as processed.')
    except InstagramWebhook.DoesNotExist:
        messages.error(request, 'Webhook not found.')
    return redirect('dashboard:instagram:webhooks')
