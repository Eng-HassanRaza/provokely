from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils.dateparse import parse_datetime

from core.models import Comment, Post, UserSettings, Device, Notification
from core.serializers import (
    CommentSerializer, CommentCreateSerializer,
    PostSerializer, PostDetailSerializer, UserSettingsSerializer, DeviceSerializer, NotificationSerializer
)
from core.services import SocialMediaService
from shared.api_responses import success_response, error_response, paginated_response
from platforms.instagram.services import InstagramService
from platforms.instagram.models import InstagramAccount


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments across all platforms
    
    Provides full CRUD operations for comments
    
    list: GET /api/v1/core/comments/
    create: POST /api/v1/core/comments/
    retrieve: GET /api/v1/core/comments/{id}/
    update: PUT /api/v1/core/comments/{id}/
    partial_update: PATCH /api/v1/core/comments/{id}/
    destroy: DELETE /api/v1/core/comments/{id}/
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform', 'sentiment_label', 'response_posted', 'requires_approval', 'approved']
    search_fields = ['content', 'external_id']
    ordering_fields = ['created_at', 'sentiment_score']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        """Restrict to current user's comments and support optional since filter."""
        qs = super().get_queryset().filter(user=self.request.user)
        since_str = self.request.query_params.get('since')
        if since_str:
            dt = parse_datetime(since_str)
            if dt is not None:
                qs = qs.filter(created_at__gte=dt)
        return qs

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve and post threaded reply for this comment (Instagram)."""
        comment = self.get_object()
        if comment.response_posted:
            serializer = self.get_serializer(comment)
            return success_response(serializer.data, 'Reply already posted')
        if comment.platform != 'instagram':
            return error_response('Only Instagram replies are supported in MVP', code='UNSUPPORTED_PLATFORM', status_code=400)
        text = request.data.get('text') or (comment.ai_response or '').strip()
        if not text:
            return error_response('Reply text is required', code='VALIDATION_ERROR', status_code=400)
        try:
            account = InstagramAccount.objects.get(user=request.user)
        except InstagramAccount.DoesNotExist:
            return error_response('Instagram not connected', code='NOT_CONNECTED', status_code=400)
        service = InstagramService()
        service.bind_access_token(account.access_token)
        try:
            service.post_reply(comment.external_id, text)
        except Exception as e:
            return error_response('Failed to post reply', code='POST_FAILED', details=str(e), status_code=502)
        # Update state
        comment.ai_response = text
        comment.response_posted = True
        comment.requires_approval = False
        comment.approved = True
        comment.save()
        # Update notification if exists
        try:
            from core.models import Notification
            notif = Notification.objects.get(user=request.user, platform='instagram', external_id=comment.external_id)
            notif.is_read = True
            notif.needs_approval = False
            notif.ai_response = text
            notif.save()
        except Exception:
            pass
        serializer = self.get_serializer(comment)
        return success_response(serializer.data, 'Reply posted')

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline approval without posting a reply; mark handled."""
        comment = self.get_object()
        if comment.response_posted:
            serializer = self.get_serializer(comment)
            return success_response(serializer.data, 'Already replied; cannot decline')
        comment.requires_approval = False
        comment.approved = False
        comment.save()
        try:
            from core.models import Notification
            notif = Notification.objects.get(user=request.user, platform=comment.platform, external_id=comment.external_id)
            notif.is_read = True
            notif.needs_approval = False
            notif.save()
        except Exception:
            pass
        serializer = self.get_serializer(comment)
        return success_response(serializer.data, 'Declined')
    
    @action(detail=True, methods=['post'])
    def analyze_sentiment(self, request, pk=None):
        """
        Analyze sentiment for a specific comment
        POST /api/v1/core/comments/{id}/analyze_sentiment/
        """
        comment = self.get_object()
        service = SocialMediaService()
        result = service.analyze_comment_sentiment(comment)
        
        return success_response(
            data={
                'comment_id': comment.id,
                'sentiment': result
            },
            message='Sentiment analyzed successfully'
        )
    
    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        """
        Get comments grouped by platform
        GET /api/v1/core/comments/by_platform/
        """
        platform = request.query_params.get('platform')
        if not platform:
            return error_response(
                message='platform parameter is required',
                code='VALIDATION_ERROR',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        comments = self.queryset.filter(platform=platform)
        serializer = self.get_serializer(comments, many=True)
        
        return success_response(
            data=serializer.data,
            message=f'Retrieved comments for {platform}'
        )


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for posts across all platforms
    
    Provides full CRUD operations for posts
    
    list: GET /api/v1/core/posts/
    create: POST /api/v1/core/posts/
    retrieve: GET /api/v1/core/posts/{id}/
    update: PUT /api/v1/core/posts/{id}/
    partial_update: PATCH /api/v1/core/posts/{id}/
    destroy: DELETE /api/v1/core/posts/{id}/
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform']
    search_fields = ['content', 'author', 'external_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Get all comments for a specific post
        GET /api/v1/core/posts/{id}/comments/
        """
        post = self.get_object()
        comments = Comment.objects.filter(
            platform=post.platform,
            external_id__startswith=post.external_id
        )
        serializer = CommentSerializer(comments, many=True)
        
        return success_response(
            data=serializer.data,
            message=f'Retrieved {comments.count()} comments'
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall statistics
        GET /api/v1/core/posts/statistics/
        """
        stats = {
            'total_posts': Post.objects.count(),
            'total_comments': Comment.objects.count(),
            'by_platform': {},
            'by_sentiment': {
                'positive': Comment.objects.filter(sentiment_label='positive').count(),
                'negative': Comment.objects.filter(sentiment_label='negative').count(),
                'neutral': Comment.objects.filter(sentiment_label='neutral').count(),
                'hate': Comment.objects.filter(sentiment_label='hate').count(),
            }
        }
        
        for platform_choice in Comment.PLATFORM_CHOICES:
            platform = platform_choice[0]
            stats['by_platform'][platform] = {
                'posts': Post.objects.filter(platform=platform).count(),
                'comments': Comment.objects.filter(platform=platform).count(),
            }
        
        return success_response(
            data=stats,
            message='Statistics retrieved successfully'
        )


class UserSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user settings
    
    Provides full CRUD operations for user preferences
    
    list: GET /api/v1/core/settings/
    create: POST /api/v1/core/settings/
    retrieve: GET /api/v1/core/settings/{id}/
    update: PUT /api/v1/core/settings/{id}/
    partial_update: PATCH /api/v1/core/settings/{id}/
    destroy: DELETE /api/v1/core/settings/{id}/
    """
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter settings by current user"""
        return UserSettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user when creating settings"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """
        Get current user's settings
        GET /api/v1/core/settings/my_settings/
        """
        try:
            settings = UserSettings.objects.get(user=request.user)
            serializer = self.get_serializer(settings)
            return success_response(
                data=serializer.data,
                message='User settings retrieved successfully'
            )
        except UserSettings.DoesNotExist:
            return error_response(
                message='User settings not found',
                code='NOT_FOUND',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def toggle_auto_comment(self, request):
        """
        Toggle auto-commenting feature
        POST /api/v1/core/settings/toggle_auto_comment/
        """
        settings, created = UserSettings.objects.get_or_create(
            user=request.user,
            defaults={'auto_comment_enabled': True}
        )


class DeviceViewSet(viewsets.ModelViewSet):
    """Register/unregister mobile devices for push notifications"""
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Device.objects.all()

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """List notifications and support read states and counts"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform', 'is_read', 'sentiment_label', 'needs_approval']
    search_fields = ['comment_text', 'external_id', 'media_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def count(self, request):
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        return success_response({'unread': unread}, 'Count fetched')

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return success_response(self.get_serializer(notif).data, 'Marked read')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return success_response({'updated': True}, 'All marked read')
        
        settings.auto_comment_enabled = not settings.auto_comment_enabled
        settings.save()
        
        return success_response(
            data={
                'auto_comment_enabled': settings.auto_comment_enabled
            },
            message=f'Auto-commenting {"enabled" if settings.auto_comment_enabled else "disabled"}'
        )
