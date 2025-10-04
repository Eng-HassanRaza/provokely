from django.contrib import admin
from platforms.instagram.models import InstagramAccount, InstagramWebhook


@admin.register(InstagramAccount)
class InstagramAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'instagram_user_id', 'followers_count', 'following_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['username', 'instagram_user_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('username', 'instagram_user_id', 'profile_picture_url')
        }),
        ('Statistics', {
            'fields': ('followers_count', 'following_count')
        }),
        ('Authentication', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InstagramWebhook)
class InstagramWebhookAdmin(admin.ModelAdmin):
    list_display = ['id', 'webhook_id', 'account', 'event_type', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['webhook_id', 'account__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Webhook Information', {
            'fields': ('webhook_id', 'account', 'event_type')
        }),
        ('Payload', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('processed',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
