from django.db import models
import uuid


class APIUser(models.Model):
    """User accounts for hosted API service"""
    id = models.CharField(max_length=255, primary_key=True)
    email = models.EmailField(unique=True, db_index=True)
    auth_token = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_requests = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    class Meta:
        db_table = 'api_users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.id})"
    
    @classmethod
    def generate_user_id(cls):
        """Generate unique user ID in format user_{timestamp}"""
        import time
        return f"user_{int(time.time() * 1000)}"


class UsageLog(models.Model):
    """Track API usage for billing and analytics"""
    api_user = models.ForeignKey(APIUser, on_delete=models.CASCADE, related_name='usage_logs')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    action = models.CharField(max_length=100, help_text="API action performed")
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    model = models.CharField(max_length=50, default='gpt-4o-mini')
    prompt_length = models.IntegerField(default=0, help_text="Character length of prompt")
    
    class Meta:
        db_table = 'usage_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['api_user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.api_user.email} - {self.action} ({self.timestamp})"

