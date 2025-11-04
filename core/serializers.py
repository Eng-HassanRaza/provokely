from rest_framework import serializers
from core.models import Post, UserSettings, Device


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model - works across all platforms"""
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'platform', 'external_id', 'content', 'author', 'url', 
                  'is_monitored', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PostDetailSerializer(PostSerializer):
    """Detailed post serializer"""
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for UserSettings model"""
    class Meta:
        model = UserSettings
        fields = ['id', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'platform', 'token', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']