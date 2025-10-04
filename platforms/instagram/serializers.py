from rest_framework import serializers
from platforms.instagram.models import InstagramAccount, InstagramWebhook


class InstagramAccountSerializer(serializers.ModelSerializer):
    """Serializer for Instagram accounts"""
    
    class Meta:
        model = InstagramAccount
        fields = ['id', 'username', 'instagram_user_id', 'profile_picture_url', 
                  'followers_count', 'following_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstagramAccountCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Instagram accounts"""
    
    class Meta:
        model = InstagramAccount
        fields = ['username', 'instagram_user_id', 'access_token', 'profile_picture_url']


class InstagramWebhookSerializer(serializers.ModelSerializer):
    """Serializer for Instagram webhooks"""
    
    class Meta:
        model = InstagramWebhook
        fields = ['id', 'webhook_id', 'account', 'event_type', 'payload', 
                  'processed', 'created_at']
        read_only_fields = ['id', 'created_at']
