from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings

from platforms.instagram.models import InstagramAccount, InstagramWebhook
from core.models import Post, UserSettings
from platforms.instagram.serializers import (
    InstagramAccountSerializer, 
    InstagramAccountCreateSerializer,
    InstagramWebhookSerializer
)
from shared.api_responses import success_response, error_response
from shared.exceptions import PlatformAPIError
from django.utils import timezone
from platforms.instagram.models import InstagramAccount
from platforms.instagram.services import InstagramService
from django.utils.crypto import get_random_string
from urllib.parse import urlencode
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt


class InstagramAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Instagram accounts
    
    Provides full CRUD operations for Instagram account management
    
    list: GET /api/v1/instagram/accounts/
    create: POST /api/v1/instagram/accounts/
    retrieve: GET /api/v1/instagram/accounts/{id}/
    update: PUT /api/v1/instagram/accounts/{id}/
    partial_update: PATCH /api/v1/instagram/accounts/{id}/
    destroy: DELETE /api/v1/instagram/accounts/{id}/
    """
    queryset = InstagramAccount.objects.all()
    serializer_class = InstagramAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InstagramAccountCreateSerializer
        return InstagramAccountSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new Instagram account"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return success_response(
            data=serializer.data,
            message="Instagram account created successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    def list(self, request, *args, **kwargs):
        """List all Instagram accounts"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return success_response(
            data=serializer.data,
            message=f"Retrieved {queryset.count()} Instagram accounts"
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific Instagram account"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return success_response(
            data=serializer.data,
            message="Instagram account retrieved successfully"
        )
    
    def update(self, request, *args, **kwargs):
        """Update an Instagram account"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return success_response(
            data=serializer.data,
            message="Instagram account updated successfully"
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete an Instagram account"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return success_response(
            data=None,
            message="Instagram account deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'])
    def sync_posts(self, request, pk=None):
        """
        Sync posts from Instagram for this account
        POST /api/v1/instagram/accounts/{id}/sync_posts/
        """
        account = self.get_object()
        
        # Ensure fresh token
        if InstagramService().should_refresh_token(account.token_created_at, account.expires_in):
            try:
                refreshed = InstagramService().refresh_user_token(account.access_token)
                account.access_token = refreshed.get('access_token', account.access_token)
                account.expires_in = refreshed.get('expires_in', account.expires_in)
                account.token_created_at = timezone.now()
                account.save()
            except PlatformAPIError:
                pass
        service = InstagramService()
        service.bind_access_token(account.access_token)
        posts = service.fetch_posts(account.instagram_user_id, limit=10)
        # Persist posts to core Post model (simplified)
        from core.models import Post
        created_count = 0
        for p in posts:
            post, created = Post.objects.get_or_create(
                platform='instagram',
                external_id=p['id'],
                defaults={
                    'user': account.user,
                    'content': p.get('caption') or '',
                    'url': p.get('permalink')
                }
            )
            if created:
                created_count += 1
        return success_response(
            data={'account_id': account.id, 'fetched': len(posts), 'created': created_count},
            message="Posts synchronized"
        )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get statistics for this Instagram account
        GET /api/v1/instagram/accounts/{id}/statistics/
        """
        account = self.get_object()
        
        stats = {
            'username': account.username,
            'followers_count': account.followers_count,
            'following_count': account.following_count,
            'is_active': account.is_active,
            'webhooks_count': account.webhooks.count()
        }
        
        return success_response(
            data=stats,
            message="Statistics retrieved successfully"
        )

    @action(detail=False, methods=['get'], url_path='mobile/auth-url')
    def mobile_auth_url(self, request):
        """Get Instagram OAuth URL for mobile app."""
        state = get_random_string(32)
        request.session['ig_mobile_state'] = state
        params = {
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'redirect_uri': settings.INSTAGRAM_MOBILE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'instagram_basic,instagram_manage_comments,pages_manage_engagement,pages_read_engagement,pages_show_list',
            'state': state,
            'display': 'page',
        }
        url = f"https://www.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/dialog/oauth?{urlencode(params)}"
        return success_response({'url': url, 'state': state}, 'Auth URL generated')

    @action(detail=False, methods=['get'], url_path='mobile/status')
    def mobile_status(self, request):
        """Return connection status for current user."""
        try:
            account = InstagramAccount.objects.get(user=request.user, is_active=True)
            
            # Get user settings for notification preferences
            try:
                settings = UserSettings.objects.get(user=request.user)
                notification_settings = {
                    'auto_comment_enabled': settings.auto_comment_enabled,
                    'notify_on_positive': settings.notify_on_positive,
                    'notify_on_negative': settings.notify_on_negative,
                    'notify_on_hate': settings.notify_on_hate,
                    'notify_on_neutral': settings.notify_on_neutral,
                    'notify_on_purchase_intent': settings.notify_on_purchase_intent,
                    'notify_on_question': settings.notify_on_question,
                }
            except UserSettings.DoesNotExist:
                notification_settings = {}
            
            data = {
                'connected': True,
                'ig_user': {
                    'id': account.instagram_user_id,
                    'username': account.username,
                    'profile_picture_url': account.profile_picture_url,
                    'followers_count': account.followers_count,
                    'account_type': account.account_type,
                },
                'notification_settings': notification_settings,
                'connected_at': account.created_at.isoformat() if account.created_at else None,
            }
        except InstagramAccount.DoesNotExist:
            data = {'connected': False}
        return success_response(data, 'Status fetched')

    @action(detail=False, methods=['post'], url_path='mobile/facebook-token')
    def facebook_token_auth(self, request):
        """
        Accept Facebook access token from mobile SDK and link Instagram account.
        This endpoint is for native mobile apps using Facebook SDK OAuth.
        
        POST /api/v1/instagram/accounts/mobile/facebook-token/
        
        Request Body:
        {
            "access_token": "EAALZBszT4wXoBOz...",
            "platform": "ios"  // optional: "ios" or "android"
        }
        
        Success Response:
        {
            "success": true,
            "data": {
                "connected": true,
                "ig_user": {
                    "id": "17841409228847394",
                    "username": "hassanjutt__"
                }
            },
            "message": "Instagram account connected successfully"
        }
        """
        # Extract and validate input
        access_token = request.data.get('access_token')
        platform = request.data.get('platform', 'unknown')
        
        if not access_token:
            return error_response(
                message="access_token is required",
                code="MISSING_TOKEN",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = InstagramService()
            
            # Step 1: Validate token using Debug Token API
            try:
                token_data = service.validate_facebook_token(access_token)
                
                if not token_data.get('is_valid'):
                    return error_response(
                        message="Facebook access token is invalid or expired",
                        code="INVALID_TOKEN",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # Verify token was issued for our app
                if str(token_data.get('app_id')) != str(settings.INSTAGRAM_CLIENT_ID):
                    return error_response(
                        message="Token was not issued for this application",
                        code="WRONG_APP",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    
            except PlatformAPIError:
                return error_response(
                    message="Facebook access token is invalid or expired",
                    code="INVALID_TOKEN",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 2: Exchange for long-lived token (recommended for 60-day validity)
            try:
                long_lived = service.get_long_lived_token(access_token)
                access_token = long_lived.get('access_token', access_token)
                expires_in = long_lived.get('expires_in')
            except Exception:
                # Continue with short-lived token if exchange fails
                expires_in = None
                if 'expires_at' in token_data:
                    # Calculate expires_in from expires_at timestamp
                    import time
                    expires_in = max(0, token_data['expires_at'] - int(time.time()))
            
            # Steps 3-5: Get Instagram account via Facebook Pages
            # This method already handles: get pages, extract page token, get IG account
            try:
                profile = service.get_user_profile(access_token)
            except PlatformAPIError as e:
                error_msg = str(e)
                
                # Map errors to specific codes
                if 'No Instagram business account found' in error_msg:
                    return error_response(
                        message="No Instagram Business Account linked to Facebook page",
                        code="NO_INSTAGRAM",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                elif 'No Facebook pages' in error_msg or 'linked to Facebook Pages' in error_msg:
                    return error_response(
                        message="No Facebook pages found. User must have a Facebook page connected.",
                        code="NO_PAGES",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                elif 'not accessible' in error_msg:
                    return error_response(
                        message="No Instagram Business Account linked to Facebook page",
                        code="NO_INSTAGRAM",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    return error_response(
                        message=error_msg,
                        code="API_ERROR",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            # Step 6: Save to database
            account, created = InstagramAccount.objects.update_or_create(
                user=request.user,
                instagram_user_id=profile['id'],
                defaults={
                    'username': profile.get('username', ''),
                    'access_token': access_token,  # This is the page access token from get_user_profile
                    'expires_in': expires_in,
                    'token_created_at': timezone.now(),
                    'account_type': profile.get('account_type', 'BUSINESS'),
                    'media_count': profile.get('media_count', 0),
                    'followers_count': profile.get('followers_count', 0),
                    'following_count': profile.get('following_count', 0),
                    'is_active': True,
                }
            )
            
            # Step 7: Return success response
            return success_response(
                data={
                    'connected': True,
                    'ig_user': {
                        'id': profile['id'],
                        'username': profile.get('username', '')
                    }
                },
                message="Instagram account connected successfully",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            # Catch any unexpected errors
            return error_response(
                message=f"Server error: {str(e)}",
                code="SERVER_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def mobile_oauth_callback(request):
    """OAuth callback for mobile apps: exchanges code, binds account, then deep-links back."""
    error = request.GET.get('error')
    if error:
        return HttpResponse("<script>location.href='provokely://oauth/instagram?status=error&reason="+error+"';</script>")
    state = request.GET.get('state')
    code = request.GET.get('code')
    if not state or state != request.session.get('ig_mobile_state'):
        return HttpResponse("<script>location.href='provokely://oauth/instagram?status=error&reason=invalid_state';</script>")
    if not code:
        return HttpResponse("<script>location.href='provokely://oauth/instagram?status=error&reason=missing_code';</script>")
    try:
        service = InstagramService()
        token_data = service.exchange_code_for_token(code, redirect_uri=settings.INSTAGRAM_MOBILE_REDIRECT_URI)
        long_lived = service.get_long_lived_token(token_data['access_token'])
        profile = service.get_user_profile(long_lived['access_token'])
        account, _ = InstagramAccount.objects.update_or_create(
            user=request.user,
            defaults={
                'instagram_user_id': profile['id'],
                'username': profile.get('username', ''),
                'access_token': long_lived['access_token'],
                'expires_in': long_lived.get('expires_in'),
                'token_created_at': timezone.now(),
                'is_active': True,
            }
        )
        return HttpResponse("<script>location.href='provokely://oauth/instagram?status=success';</script>")
    except Exception as e:
        return HttpResponse("<script>location.href='provokely://oauth/instagram?status=error&reason=server';</script>")


from django.http import HttpResponse


class InstagramWebhookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Instagram webhooks (read-only)
    
    list: GET /api/v1/instagram/webhooks/
    retrieve: GET /api/v1/instagram/webhooks/{id}/
    """
    queryset = InstagramWebhook.objects.all()
    serializer_class = InstagramWebhookSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Allow Facebook webhook verification and event delivery without auth
        if self.action in ['verify_subscription', 'receive_update']:
            return [AllowAny()]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """List all webhooks"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return success_response(
            data=serializer.data,
            message=f"Retrieved {queryset.count()} webhooks"
        )
    
    @action(detail=True, methods=['post'])
    def mark_processed(self, request, pk=None):
        """
        Mark a webhook as processed
        POST /api/v1/instagram/webhooks/{id}/mark_processed/
        """
        webhook = self.get_object()
        webhook.processed = True
        webhook.save()
        
        return success_response(
            data={'webhook_id': webhook.id, 'processed': True},
            message="Webhook marked as processed"
        )

    @action(detail=False, methods=['get', 'post'], url_path='verify')
    def verify_subscription(self, request):
        """Unified endpoint for GET verification and POST deliveries (if Meta posts to same URL)."""
        if request.method.lower() == 'get':
            mode = request.query_params.get('hub.mode')
            token = request.query_params.get('hub.verify_token')
            challenge = request.query_params.get('hub.challenge')
            verify_token = getattr(settings, 'FACEBOOK_WEBHOOK_VERIFY_TOKEN', None)
            if mode == 'subscribe' and token and verify_token and token == verify_token:
                return HttpResponse(challenge, content_type='text/plain', status=200)
            return error_response("Webhook verification failed", status_code=status.HTTP_403_FORBIDDEN)
        # Handle POST delivery same as receive_update
        payload = request.data
        # Fallback: some deliveries come as form-encoded with 'object' and 'entry' string
        if not isinstance(payload, dict) or ('entry' not in payload and request.body):
            try:
                import json
                payload = json.loads(request.body.decode('utf-8'))
            except Exception:
                payload = {}
        created = []
        try:
            for entry in payload.get('entry', []):
                entry_ig_user_id = entry.get('id')  # IG Business Account ID
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    ig_user_id = entry_ig_user_id
                    if not ig_user_id:
                        continue
                    try:
                        account = InstagramAccount.objects.get(instagram_user_id=ig_user_id)
                    except InstagramAccount.DoesNotExist:
                        continue
                    event_type = change.get('field', 'instagram')
                    comment_id = value.get('id') or value.get('comment_id')
                    media_id = (value.get('media') or {}).get('id') or value.get('media_id')
                    unique_id = comment_id or media_id or f"{entry.get('time','')}-{event_type}"
                    # Optional debug
                    if settings.DEBUG:
                        print("Webhook POST (verify)", {
                            'ig_user_id': ig_user_id,
                            'event_type': event_type,
                            'comment_id': comment_id,
                            'media_id': media_id,
                        })
                    webhook = account.webhooks.create(
                        webhook_id=str(unique_id),
                        event_type=event_type,
                        payload=value
                    )
                    created.append(webhook.id)
                    # Auto-process comment events
                    if event_type == 'comments' and comment_id:
                        try:
                            # Sentiment + auto-reply based on settings
                            settings_obj = UserSettings.objects.get(user=account.user)
                            service = InstagramService()
                            service.bind_access_token(account.access_token)
                            detail = service.fetch_comment_detail(comment_id)
                            text = detail.get('text', '')
                            # Process comment into core table, with idempotency
                            result = service.core_service.process_comment(
                                comment_text=text,
                                platform='instagram',
                                external_id=comment_id,
                                user=account.user,
                                post_id=media_id
                            )
                            label = result['sentiment'].get('label')
                            # Determine if approval is required
                            needs_approval = False
                            if settings_obj.auto_comment_enabled:
                                if label == 'negative' and settings_obj.require_approval_for_negative:
                                    needs_approval = True
                                if label == 'hate' and settings_obj.require_approval_for_hate:
                                    needs_approval = True
                            # Notification preferences
                            should_notify = (
                                (label == 'positive' and settings_obj.notify_on_positive) or
                                (label == 'negative' and settings_obj.notify_on_negative) or
                                (label == 'hate' and settings_obj.notify_on_hate) or
                                (label == 'neutral' and settings_obj.notify_on_neutral)
                            )
                            notif, _ = Notification.objects.update_or_create(
                                user=account.user,
                                platform='instagram',
                                external_id=comment_id,
                                defaults={
                                    'media_id': media_id,
                                    'comment_text': text,
                                    'sentiment_label': label,
                                    'needs_approval': needs_approval,
                                    'ai_response': result.get('ai_response'),
                                    'is_read': False,
                                }
                            )
                            # Push to SSE subscribers
                            try:
                                payload = {
                                    'unread_count': Notification.objects.filter(user=account.user, is_read=False).count(),
                                    'latest': {
                                        'id': notif.id,
                                        'text': text,
                                        'label': label,
                                        'needs_approval': needs_approval,
                                    }
                                }
                                import json
                                publish(account.user.id, json.dumps(payload))
                            except Exception:
                                pass
                            # Send mobile push (FCM)
                            try:
                                PushService().notify_new_notification(account.user, notif)
                            except Exception:
                                pass
                        except Exception as e:
                            if settings.DEBUG:
                                print('Webhook auto-process error:', str(e))
            return success_response({'created': len(created)}, "Webhook received")
        except Exception as e:
            # Do not block webhook delivery on parse errors; log and ack 200
            if settings.DEBUG:
                print("Webhook verify POST parse error:", str(e))
                try:
                    print("Raw body:", request.body[:500])
                except Exception:
                    pass
            return HttpResponse(status=200)

    @action(detail=False, methods=['post'], url_path='receive', permission_classes=[AllowAny])
    def receive_update(self, request):
        """Receive webhook events and store them."""
        payload = request.data
        if not isinstance(payload, dict) or ('entry' not in payload and request.body):
            try:
                import json
                payload = json.loads(request.body.decode('utf-8'))
            except Exception:
                payload = {}
        # Basic shape: {"entry":[{"id":"<ig_ba_id>","changes":[{"field":"comments","value":{...}}]}]}
        created = []
        try:
            for entry in payload.get('entry', []):
                entry_ig_user_id = entry.get('id')
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    ig_user_id = entry_ig_user_id
                    if not ig_user_id:
                        continue
                    try:
                        account = InstagramAccount.objects.get(instagram_user_id=ig_user_id)
                    except InstagramAccount.DoesNotExist:
                        continue
                    event_type = change.get('field', 'instagram')
                    comment_id = value.get('id') or value.get('comment_id')
                    media_id = (value.get('media') or {}).get('id') or value.get('media_id')
                    unique_id = comment_id or media_id or f"{entry.get('time','')}-{event_type}"
                    if settings.DEBUG:
                        print("Webhook POST (receive)", {
                            'ig_user_id': ig_user_id,
                            'event_type': event_type,
                            'comment_id': comment_id,
                            'media_id': media_id,
                        })
                    webhook = account.webhooks.create(
                        webhook_id=str(unique_id),
                        event_type=event_type,
                        payload=value
                    )
                    created.append(webhook.id)
            return success_response({'created': len(created)}, "Webhook received")
        except Exception as e:
            if settings.DEBUG:
                print("Webhook receive POST parse error:", str(e))
                try:
                    print("Raw body:", request.body[:500])
                except Exception:
                    pass
            return HttpResponse(status=200)
