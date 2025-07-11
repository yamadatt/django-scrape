from django.contrib import admin
from .models import ScrapingTarget, ScrapedData, ScrapingJob


@admin.register(ScrapingTarget)
class ScrapingTargetAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'enable_crawling', 'max_depth', 'max_pages', 'created_at']
    list_filter = ['is_active', 'enable_crawling', 'created_at']
    search_fields = ['name', 'url']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本設定', {
            'fields': ('name', 'url', 'css_selector', 'is_active')
        }),
        ('クロール設定', {
            'fields': ('enable_crawling', 'max_depth', 'max_pages', 'link_selector', 'allowed_domains', 'exclude_patterns'),
            'description': 'サイト全体をクロールする場合の設定'
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    list_display = ['target', 'title', 'url', 'depth', 'scraped_at']
    list_filter = ['target', 'depth', 'scraped_at']
    search_fields = ['title', 'content', 'url']
    readonly_fields = ['scraped_at']
    date_hierarchy = 'scraped_at'


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ['target', 'status', 'started_at', 'completed_at', 'items_scraped']
    list_filter = ['status', 'target', 'started_at']
    readonly_fields = ['started_at', 'completed_at']
    date_hierarchy = 'started_at'