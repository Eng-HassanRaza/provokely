from django.db import transaction
from django.contrib.auth.models import User
from core.models import Comment, Post, UserSettings, Device
from django.conf import settings
from core.sentiment import SentimentAnalyzer
from core.responses import ResponseGenerator


class SocialMediaService:
    """Main service for processing social media content"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.response_generator = ResponseGenerator()
    
    @transaction.atomic
    def process_comment(self, comment_text: str, platform: str, external_id: str, user: User, post_id: str = None):
        """
        Process a comment and generate AI response based on user settings
        
        Args:
            comment_text: The comment content
            platform: Platform name (instagram, facebook, etc.)
            external_id: Platform-specific comment ID
            user: User who owns the post
            post_id: Optional post ID this comment belongs to
        
        Returns:
            dict: Processing result with comment and response
        """
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(comment_text)
        
        # Get user settings
        try:
            settings = UserSettings.objects.get(user=user)
        except UserSettings.DoesNotExist:
            settings = UserSettings.objects.create(user=user)
        
        # Create or update comment
        comment, created = Comment.objects.update_or_create(
            platform=platform,
            external_id=external_id,
            defaults={
                'user': user,
                'content': comment_text,
                'sentiment_score': sentiment['score'],
                'sentiment_label': sentiment['label']
            }
        )
        
        # Determine if response is needed based on user settings
        should_respond = self._should_generate_response(sentiment, settings)
        
        if should_respond:
            # Determine if this sentiment requires approval when auto-reply is enabled
            label = (sentiment.get('label') or '').lower()
            needs_approval = False
            if settings.auto_comment_enabled:
                if label == 'negative' and settings.require_approval_for_negative:
                    needs_approval = True
                if label == 'hate' and settings.require_approval_for_hate:
                    needs_approval = True

            ai_response = self.response_generator.generate(sentiment, platform, comment_text)
            comment.ai_response = ai_response

            if settings.auto_comment_enabled and not needs_approval:
                # Post immediately (no approval required for this sentiment)
                comment.requires_approval = False
                if platform == 'instagram':
                    try:
                        from platforms.instagram.models import InstagramAccount
                        from platforms.instagram.services import InstagramService
                        from django.utils import timezone
                        account = InstagramAccount.objects.get(user=user)
                        service = InstagramService()
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
                        service.post_reply(external_id, ai_response)
                        comment.response_posted = True
                    except Exception:
                        comment.response_posted = False
            else:
                # Either auto-reply off, or approval required for this sentiment: do not post now
                comment.requires_approval = True if settings.auto_comment_enabled and needs_approval else False
            
            comment.save()
        
        return {
            'comment': comment,
            'sentiment': sentiment,
            'ai_response': comment.ai_response,
            'requires_approval': comment.requires_approval,
            'created': created
        }


    def analyze_comment_sentiment(self, comment: Comment):
        """Re-analyze sentiment for an existing comment"""
        sentiment = self.sentiment_analyzer.analyze(comment.content)
        
        comment.sentiment_score = sentiment['score']
        comment.sentiment_label = sentiment['label']
        comment.save()
        
        return sentiment
    
    @transaction.atomic
    def create_post(self, platform: str, external_id: str, content: str, user: User, **kwargs):
        """Create a new post"""
        post, created = Post.objects.get_or_create(
            platform=platform,
            external_id=external_id,
            defaults={
                'user': user,
                'content': content,
                **kwargs
            }
        )
        return post
    
    def _should_generate_response(self, sentiment: dict, settings: UserSettings) -> bool:
        """Determine if a response should be generated based on sentiment and settings"""
        label = sentiment.get('label')
        
        if label == 'positive' and settings.auto_respond_to_positive:
            return True
        elif label == 'negative' and settings.auto_respond_to_negative:
            return True
        elif label == 'hate' and settings.auto_respond_to_hate:
            return True
        
        return False
    
    def _requires_approval(self, sentiment: dict, settings: UserSettings) -> bool:
        """Determine if approval is required based on sentiment and settings"""
        label = sentiment.get('label')
        
        if label == 'hate' and settings.require_approval_for_hate:
            return True
        elif label == 'negative' and settings.require_approval_for_negative:
            return True
        
        return False
    
    def approve_comment_response(self, comment_id: int) -> bool:
        """Approve and post a comment response"""
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.approved = True
            comment.response_posted = True
            comment.save()
            return True
        except Comment.DoesNotExist:
            return False
    
    def reject_comment_response(self, comment_id: int) -> bool:
        """Reject a comment response"""
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.approved = False
            comment.ai_response = None
            comment.save()
            return True
        except Comment.DoesNotExist:
            return False


class PushService:
    """Send push notifications to registered devices via FCM (Android first)."""
    def __init__(self):
        self.enabled = bool(getattr(settings, 'FCM_SERVER_KEY', None))
        self._client = None
        if self.enabled:
            try:
                from pyfcm import FCMNotification
                self._client = FCMNotification(api_key=settings.FCM_SERVER_KEY)
            except Exception:
                self.enabled = False

    def notify_new_notification(self, user, notification):
        if not self.enabled:
            return
        try:
            tokens = list(Device.objects.filter(user=user, platform='android').values_list('token', flat=True))
            if not tokens:
                return
            title = f"{notification.sentiment_label or 'New'} comment"
            body = (notification.comment_text or '')[:120]
            data_message = {
                'type': 'comment',
                'notification_id': str(notification.id),
                'comment_id': notification.external_id,
                'category': notification.sentiment_label or '',
                'media_id': notification.media_id or '',
            }
            self._client.notify_multiple_devices(
                registration_ids=tokens,
                message_title=title,
                message_body=body,
                data_message=data_message,
                sound='default'
            )
        except Exception:
            pass
