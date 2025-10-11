from django.contrib import admin
from api_hosted.models import APIUser, UsageLog


@admin.register(APIUser)
class APIUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'is_pro', 'projects_remaining', 'total_requests', 'total_cost', 'created_at']
    list_filter = ['created_at', 'is_pro']
    search_fields = ['email', 'id', 'subscription_id', 'stripe_customer_id']
    readonly_fields = ['id', 'created_at', 'auth_token']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'email', 'created_at')
        }),
        ('Subscription', {
            'fields': ('is_pro', 'projects_remaining', 'subscription_id', 'stripe_customer_id')
        }),
        ('Usage Statistics', {
            'fields': ('total_requests', 'total_tokens_used', 'total_cost')
        }),
        ('Authentication', {
            'fields': ('auth_token',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'api_user', 'action', 'tokens_used', 'cost', 'model', 'timestamp']
    list_filter = ['action', 'model', 'timestamp']
    search_fields = ['api_user__email', 'action']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Log Information', {
            'fields': ('api_user', 'action', 'timestamp')
        }),
        ('Usage Details', {
            'fields': ('tokens_used', 'cost', 'model', 'prompt_length')
        }),
    )

