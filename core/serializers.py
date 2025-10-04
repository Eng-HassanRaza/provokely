from rest_framework import serializers
from core.models import Comment, Post, UserSettings, Device, Notification


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model - works across all platforms"""
    class Meta:
        model = Comment
        fields = ['id', 'user', 'platform', 'external_id', 'content', 'sentiment_score', 
                  'sentiment_label', 'ai_response', 'response_posted', 'requires_approval', 
                  'approved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'sentiment_score', 'sentiment_label', 'ai_response', 
                            'created_at', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    class Meta:
        model = Comment
        fields = ['platform', 'external_id', 'content']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model - works across all platforms"""
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'platform', 'external_id', 'content', 'author', 'url', 
                  'is_monitored', 'comments_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return Comment.objects.filter(
            platform=obj.platform, 
            external_id__startswith=obj.external_id
        ).count()


class PostDetailSerializer(PostSerializer):
    """Detailed post serializer with comments"""
    comments = CommentSerializer(many=True, read_only=True, source='get_comments')
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for UserSettings model"""
    class Meta:
        model = UserSettings
        fields = ['id', 'user', 'auto_comment_enabled', 'require_approval_for_hate', 
                  'require_approval_for_negative', 'auto_respond_to_positive', 
                  'auto_respond_to_negative', 'auto_respond_to_hate', 'response_style',
                  'notify_on_positive', 'notify_on_negative', 'notify_on_hate', 'notify_on_neutral',
                  'notify_on_purchase_intent', 'notify_on_question',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'platform', 'token', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'platform', 'external_id', 'media_id', 'comment_text',
            'sentiment_label', 'needs_approval', 'ai_response', 'is_read',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
