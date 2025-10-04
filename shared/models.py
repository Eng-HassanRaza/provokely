"""
Abstract base models for platform-specific extensions
"""
from django.db import models


class BaseComment(models.Model):
    """Abstract base model for platform-specific comments if needed"""
    external_id = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class BasePost(models.Model):
    """Abstract base model for platform-specific posts if needed"""
    external_id = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class BasePlatformAccount(models.Model):
    """Abstract base model for platform accounts"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='%(class)s_accounts')
    username = models.CharField(max_length=100)
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500, null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
