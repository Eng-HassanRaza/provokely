from django.contrib import admin
from shopify_integration.models import ShopifyStore, JudgeReview


@admin.register(ShopifyStore)
class ShopifyStoreAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'shop_domain', 'user', 'is_active', 'installed_at']
    list_filter = ['is_active', 'installed_at']
    search_fields = ['store_name', 'shop_domain', 'user__username']
    readonly_fields = ['installed_at']
    
    fieldsets = (
        ('Store Information', {
            'fields': ('user', 'shop_domain', 'store_name', 'is_active')
        }),
        ('Branding', {
            'fields': ('logo_url', 'primary_color')
        }),
        ('Technical', {
            'fields': ('access_token',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('installed_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(JudgeReview)
class JudgeReviewAdmin(admin.ModelAdmin):
    list_display = ['product_title', 'rating', 'reviewer_name', 'shopify_store', 'processed', 'created_at']
    list_filter = ['rating', 'processed', 'created_at', 'shopify_store']
    search_fields = ['product_title', 'reviewer_name', 'body', 'review_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('shopify_store', 'review_id', 'rating', 'title', 'body', 'reviewer_name')
        }),
        ('Product Information', {
            'fields': ('product_title', 'product_image_url')
        }),
        ('Processing', {
            'fields': ('processed',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )