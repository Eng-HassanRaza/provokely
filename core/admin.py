from django.contrib import admin
from core.models import Comment, Post


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'platform', 'content_preview', 'sentiment_label', 'sentiment_score', 'response_posted', 'created_at']
    list_filter = ['platform', 'sentiment_label', 'response_posted', 'created_at']
    search_fields = ['content', 'external_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('platform', 'external_id', 'content')
        }),
        ('Sentiment Analysis', {
            'fields': ('sentiment_score', 'sentiment_label')
        }),
        ('AI Response', {
            'fields': ('ai_response', 'response_posted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
