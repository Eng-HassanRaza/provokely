from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """Generic post model for all platforms"""
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('twitter', 'Twitter'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, db_index=True)
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


class InstagramPost(models.Model):
    """Track Instagram posts created from reviews"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating Image'),
        ('posting', 'Posting to Instagram'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instagram_posts')
    instagram_account = models.ForeignKey('instagram.InstagramAccount', on_delete=models.CASCADE)
    review_id = models.CharField(max_length=255)  # JudgeMe review ID
    shopify_store = models.ForeignKey('shopify_integration.ShopifyStore', on_delete=models.CASCADE, null=True, blank=True)
    
    # Image data
    image_url = models.URLField()
    generated_image_path = models.CharField(max_length=500, null=True, blank=True)
    
    # Post data
    caption = models.TextField()
    instagram_media_id = models.CharField(max_length=100, null=True, blank=True)
    instagram_permalink = models.URLField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'instagram_posts'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['review_id']),
            models.Index(fields=['instagram_media_id']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Instagram Post - {self.review_id} ({self.status})"


class UserSettings(models.Model):
    """User preferences for app behavior"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
    
    def __str__(self):
        return f"Settings for {self.user.username}"


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
