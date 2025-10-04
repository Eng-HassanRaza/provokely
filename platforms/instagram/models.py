from django.db import models
from django.utils import timezone
from shared.models import BasePlatformAccount


class InstagramAccount(BasePlatformAccount):
    """Instagram-specific account model"""
    instagram_user_id = models.CharField(max_length=100, unique=True)
    profile_picture_url = models.URLField(null=True, blank=True)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    
    # OAuth tokens
    access_token = models.TextField(help_text="Instagram access token")
    token_type = models.CharField(max_length=50, default='bearer')
    expires_in = models.IntegerField(null=True, blank=True, help_text="Token expiration in seconds")
    token_created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True, help_text="Refresh token if available")
    
    # Instagram API data
    account_type = models.CharField(max_length=20, default='PERSONAL', choices=[
        ('PERSONAL', 'Personal Account'),
        ('BUSINESS', 'Business Account'),
    ])
    media_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'instagram_accounts'
        verbose_name = 'Instagram Account'
        verbose_name_plural = 'Instagram Accounts'
    
    def __str__(self):
        return f"@{self.username}"


class InstagramWebhook(models.Model):
    """Track Instagram webhooks for real-time updates"""
    webhook_id = models.CharField(max_length=100, unique=True)
    account = models.ForeignKey(InstagramAccount, on_delete=models.CASCADE, related_name='webhooks')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'instagram_webhooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
