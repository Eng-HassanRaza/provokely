from django.contrib import admin
from api_hosted.models import APIUser, UsageLog


@admin.register(APIUser)
class APIUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'total_requests', 'total_tokens_used', 'total_cost', 'created_at']
    list_filter = ['created_at']
    search_fields = ['email', 'id']
    readonly_fields = ['id', 'created_at', 'auth_token']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'email', 'created_at')
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

