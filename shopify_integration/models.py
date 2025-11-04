from django.db import models
from django.contrib.auth.models import User


class ShopifyStore(models.Model):
    """Shopify store connection"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopify_stores')
    shop_domain = models.CharField(max_length=255, unique=True)
    access_token = models.TextField()
    
    # Store branding
    store_name = models.CharField(max_length=255)
    logo_url = models.URLField(null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#000000')
    
    is_active = models.BooleanField(default=True)
    installed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shopify_stores'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['shop_domain']),
        ]
        ordering = ['-installed_at']
    
    def __str__(self):
        return f"{self.store_name} ({self.shop_domain})"


class JudgeReview(models.Model):
    """JudgeMe review from Shopify store"""
    shopify_store = models.ForeignKey(ShopifyStore, on_delete=models.CASCADE, related_name='reviews')
    review_id = models.CharField(max_length=255, unique=True)
    
    # Review data from JudgeMe
    rating = models.IntegerField()
    title = models.CharField(max_length=500, null=True, blank=True)
    body = models.TextField()
    reviewer_name = models.CharField(max_length=255)
    
    # Product info
    product_title = models.CharField(max_length=500)
    product_image_url = models.URLField(null=True, blank=True)
    
    # Processing status
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'judge_reviews'
        indexes = [
            models.Index(fields=['shopify_store', 'processed']),
            models.Index(fields=['review_id']),
            models.Index(fields=['rating']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_title} - {self.rating}/5 by {self.reviewer_name}"