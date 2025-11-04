from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from core.models import Post, UserSettings, Device
from core.serializers import (
    PostSerializer, PostDetailSerializer, UserSettingsSerializer, DeviceSerializer
)
from shared.api_responses import success_response, error_response


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
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall statistics
        GET /api/v1/core/posts/statistics/
        """
        stats = {
            'total_posts': Post.objects.count(),
            'by_platform': {},
        }
        
        for platform_choice in Post.PLATFORM_CHOICES:
            platform = platform_choice[0]
            stats['by_platform'][platform] = {
                'posts': Post.objects.filter(platform=platform).count(),
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


class DeviceViewSet(viewsets.ModelViewSet):
    """Register/unregister mobile devices for push notifications"""
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Device.objects.all()

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)