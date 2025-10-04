from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    """Generic comment model for all platforms"""
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('twitter', 'Twitter'),
    ]
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('hate', 'Hate'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, db_index=True)
    external_id = models.CharField(max_length=100)
    content = models.TextField()
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, null=True, blank=True, db_index=True)
    ai_response = models.TextField(null=True, blank=True)
    response_posted = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    approved = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        indexes = [
            models.Index(fields=['platform', 'external_id']),
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['sentiment_label', 'requires_approval']),
        ]
        unique_together = ['platform', 'external_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform} - {self.content[:50]}"


class Post(models.Model):
    """Generic post model for all platforms"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    platform = models.CharField(max_length=20, choices=Comment.PLATFORM_CHOICES, db_index=True)
    external_id = models.CharField(max_length=100)
    content = models.TextField()
    author = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    is_monitored = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['platform', 'is_monitored']),
        ]
        unique_together = ['platform', 'external_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform} - {self.content[:50]}"
    
    def get_comments(self):
        """Get all comments for this post"""
        return Comment.objects.filter(platform=self.platform, external_id__startswith=self.external_id)


class UserSettings(models.Model):
    """User preferences for auto-commenting behavior"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    auto_comment_enabled = models.BooleanField(default=False)
    require_approval_for_hate = models.BooleanField(default=True)
    require_approval_for_negative = models.BooleanField(default=False)
    auto_respond_to_positive = models.BooleanField(default=True)
    auto_respond_to_negative = models.BooleanField(default=True)
    auto_respond_to_hate = models.BooleanField(default=True)
    response_style = models.CharField(
        max_length=20,
        choices=[
            ('professional', 'Professional'),
            ('casual', 'Casual'),
            ('controversial', 'Controversial'),
            ('sarcastic', 'Sarcastic'),
        ],
        default='professional'
    )
    # Notification preferences by category
    notify_on_positive = models.BooleanField(default=False)
    notify_on_negative = models.BooleanField(default=True)
    notify_on_hate = models.BooleanField(default=True)
    notify_on_neutral = models.BooleanField(default=False)
    notify_on_purchase_intent = models.BooleanField(default=True)
    notify_on_question = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
    
    def __str__(self):
        return f"Settings for {self.user.username}"


class Notification(models.Model):
    """Notification entries for comments that match user preferences or require approval"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    platform = models.CharField(max_length=20, choices=Comment.PLATFORM_CHOICES, db_index=True)
    external_id = models.CharField(max_length=100, help_text="Comment ID or unique external identifier", db_index=True)
    media_id = models.CharField(max_length=100, null=True, blank=True)
    comment_text = models.TextField(blank=True)
    sentiment_label = models.CharField(max_length=20, choices=Comment.SENTIMENT_CHOICES, null=True, blank=True)
    needs_approval = models.BooleanField(default=False)
    ai_response = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['user', 'is_read']),
        ]
        ordering = ['-created_at']
        unique_together = ['user', 'platform', 'external_id']
    
    def __str__(self):
        return f"Notification({self.platform}:{self.external_id})"


class Device(models.Model):
    """Mobile push device registration per user"""
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    platform = models.CharField(max_length=16, choices=PLATFORM_CHOICES, db_index=True)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'devices'
        indexes = [
            models.Index(fields=['user', 'platform']),
        ]
        unique_together = ['user', 'platform', 'token']
        ordering = ['-created_at']

    def __str__(self):
        return f"Device({self.user_id}:{self.platform})"
