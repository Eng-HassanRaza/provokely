from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from core.models import Comment, Post, UserSettings, Notification
from platforms.instagram.models import InstagramAccount
from platforms.instagram.services import InstagramService
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest, StreamingHttpResponse
from core.notify import subscribe, unsubscribe, publish


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
    
    # Get recent comments
    recent_comments = Comment.objects.filter(user=request.user).order_by('-created_at')[:10]
    # Notifications count
    notifications_unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Get user settings
    try:
        user_settings = UserSettings.objects.get(user=request.user)
    except UserSettings.DoesNotExist:
        user_settings = UserSettings.objects.create(user=request.user)
    
    # Webhook-only mode: do not fetch/process comments here
    ig_latest_post = None
    ig_latest_comments = []
    ig_analyzed_comments = []
    pending_approvals_count = 0

    context = {
        'instagram_connected': instagram_connected,
        'instagram_username': instagram_username,
        'recent_comments': recent_comments,
        'user_settings': user_settings,
        'notifications_unread_count': notifications_unread_count,
        # Dashboard now shows notifications only
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    if request.method == 'POST':
        # Mark read or approve-post inline could be wired here later
        ids = request.POST.getlist('ids')
        Notification.objects.filter(user=request.user, id__in=ids).update(is_read=True)
        messages.success(request, 'Notifications marked as read.')
        return redirect('dashboard:notifications')
    context = {
        'notifications': notifications,
        'notifications_unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'dashboard/notifications.html', context)


@login_required
def notifications_poll(request):
    """Server-Sent Events (SSE) stream for push notifications."""
    q = subscribe(request.user.id)
    def event_stream():
        try:
            # Send initial unread count
            unread = Notification.objects.filter(user=request.user, is_read=False).count()
            yield f"data: {{\"unread_count\": {unread}}}\n\n"
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        finally:
            unsubscribe(request.user.id, q)
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response

@login_required
@require_POST
def approve_ai_reply(request):
    """Approve and post an AI reply for a given Instagram comment on a specific media."""
    comment_id = request.POST.get('comment_id')
    media_id = request.POST.get('media_id')
    text = request.POST.get('text')
    if not all([comment_id, media_id, text]):
        return HttpResponseBadRequest("Missing required fields")
    try:
        account = InstagramAccount.objects.get(user=request.user)
        service = InstagramService()
        # Token refresh if needed
        if service.should_refresh_token(account.token_created_at, account.expires_in):
            try:
                refreshed = service.refresh_user_token(account.access_token)
                account.access_token = refreshed.get('access_token', account.access_token)
                account.expires_in = refreshed.get('expires_in', account.expires_in)
                account.token_created_at = timezone.now()
                account.save()
            except Exception:
                pass
        service.bind_access_token(account.access_token)
        # Post as a reply under the comment (threaded), or change to post_comment(media_id, text) for top-level
        result = service.post_reply(comment_id, text)
        # Mark this comment as responded to avoid re-approval prompts
        try:
            existing = Comment.objects.get(user=account.user, platform='instagram', external_id=comment_id)
            existing.ai_response = text
            existing.response_posted = True
            existing.requires_approval = False
            existing.approved = True
            existing.save()
        except Comment.DoesNotExist:
            # Create minimal record if it didn't exist for idempotency
            Comment.objects.create(
                user=account.user,
                platform='instagram',
                external_id=comment_id,
                content='',
                ai_response=text,
                response_posted=True,
                requires_approval=False,
                approved=True,
            )
        # Also mark notification as read/handled
        try:
            Notification.objects.filter(user=account.user, platform='instagram', external_id=comment_id).update(is_read=True, needs_approval=False)
        except Exception:
            pass
        messages.success(request, 'Reply posted to Instagram.')
        return redirect('dashboard:notifications')
    except InstagramAccount.DoesNotExist:
        messages.error(request, 'Instagram account not connected')
        return redirect('dashboard:notifications')
    except Exception as e:
        messages.error(request, f'Failed to post reply: {str(e)}')
        return redirect('dashboard:notifications')


@login_required
def dashboard_accounts(request):
    """Connected accounts management page"""
    # Get all connected accounts
    instagram_accounts = InstagramAccount.objects.filter(user=request.user)
    
    context = {
        'instagram_accounts': instagram_accounts,
    }
    
    return render(request, 'dashboard/accounts.html', context)


@login_required
def dashboard_settings(request):
    """User settings page"""
    try:
        user_settings = UserSettings.objects.get(user=request.user)
    except UserSettings.DoesNotExist:
        user_settings = UserSettings.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update settings
        user_settings.auto_comment_enabled = request.POST.get('auto_comment_enabled') == 'on'
        user_settings.require_approval_for_hate = request.POST.get('require_approval_for_hate') == 'on'
        user_settings.require_approval_for_negative = request.POST.get('require_approval_for_negative') == 'on'
        user_settings.auto_respond_to_positive = request.POST.get('auto_respond_to_positive') == 'on'
        user_settings.auto_respond_to_negative = request.POST.get('auto_respond_to_negative') == 'on'
        user_settings.auto_respond_to_hate = request.POST.get('auto_respond_to_hate') == 'on'
        user_settings.response_style = request.POST.get('response_style', 'professional')
        user_settings.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('dashboard:settings')
    
    context = {
        'user_settings': user_settings,
    }
    
    return render(request, 'dashboard/settings.html', context)


@login_required
def dashboard_profile(request):
    """User profile page"""
    if request.method == 'POST':
        # Update profile
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard:profile')
    
    context = {
        'user': request.user,
    }
    
    return render(request, 'dashboard/profile.html', context)


