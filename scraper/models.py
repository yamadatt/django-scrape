from django.db import models
from django.utils import timezone


class ScrapingTarget(models.Model):
    """スクレイピング対象サイトの設定"""
    name = models.CharField('サイト名', max_length=200)
    url = models.URLField('URL')
    css_selector = models.TextField('CSSセレクタ', help_text='取得したいデータのCSSセレクタ')
    is_active = models.BooleanField('有効', default=True)
    
    # クロール設定
    enable_crawling = models.BooleanField('サイト全体クロール', default=False, help_text='有効にするとサイト全体をクロールします')
    max_depth = models.IntegerField('最大深度', default=2, help_text='クロールする最大深度（1=トップページのみ）')
    max_pages = models.IntegerField('最大ページ数', default=50, help_text='クロールする最大ページ数')
    link_selector = models.TextField('リンクセレクタ', default='a[href]', help_text='クロール対象のリンクを指定するCSSセレクタ')
    allowed_domains = models.TextField('許可ドメイン', blank=True, help_text='クロール対象ドメイン（空白の場合は同一ドメインのみ）')
    exclude_patterns = models.TextField('除外パターン', blank=True, help_text='除外するURLパターン（改行区切り）')
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'スクレイピング対象'
        verbose_name_plural = 'スクレイピング対象'

    def __str__(self):
        return self.name


class ScrapedData(models.Model):
    """スクレイピングで取得したデータ"""
    target = models.ForeignKey(ScrapingTarget, on_delete=models.CASCADE, verbose_name='対象サイト')
    title = models.CharField('タイトル', max_length=2000, blank=True)
    content = models.TextField('内容')
    url = models.URLField('URL', max_length=500, blank=True)
    depth = models.IntegerField('クロール深度', default=0, help_text='0=開始ページ、1=1階層下、など')
    scraped_at = models.DateTimeField('取得日時', default=timezone.now)
    
    class Meta:
        verbose_name = 'スクレイピングデータ'
        verbose_name_plural = 'スクレイピングデータ'
        ordering = ['-scraped_at']

    def __str__(self):
        return f"{self.target.name} - {self.title or '無題'}"


class ScrapingJob(models.Model):
    """スクレイピングジョブの管理"""
    STATUS_CHOICES = [
        ('pending', '待機中'),
        ('running', '実行中'),
        ('completed', '完了'),
        ('failed', '失敗'),
    ]
    
    target = models.ForeignKey(ScrapingTarget, on_delete=models.CASCADE, verbose_name='対象サイト')
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField('開始日時', null=True, blank=True)
    completed_at = models.DateTimeField('完了日時', null=True, blank=True)
    error_message = models.TextField('エラーメッセージ', blank=True)
    items_scraped = models.IntegerField('取得件数', default=0)
    
    class Meta:
        verbose_name = 'スクレイピングジョブ'
        verbose_name_plural = 'スクレイピングジョブ'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.target.name} - {self.get_status_display()}" 