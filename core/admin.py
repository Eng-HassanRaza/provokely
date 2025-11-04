from django.contrib import admin
from core.models import Post, InstagramPost, UserSettings, Device


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'platform', 'content_preview', 'author', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['content', 'author', 'external_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('platform', 'external_id', 'content', 'author', 'url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'review_id', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['review_id', 'caption', 'instagram_media_id']
    readonly_fields = ['created_at', 'posted_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'instagram_account', 'review_id', 'shopify_store')
        }),
        ('Image Data', {
            'fields': ('image_url', 'generated_image_path')
        }),
        ('Post Data', {
            'fields': ('caption', 'instagram_media_id', 'instagram_permalink')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'posted_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['user__username', 'token']
    readonly_fields = ['created_at', 'updated_at']
