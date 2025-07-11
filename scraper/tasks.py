from celery import shared_task
from django.utils import timezone
from .models import ScrapingTarget, ScrapedData, ScrapingJob
from .scraping_utils import ScrapingEngine, detect_scraping_method
from .crawler import WebCrawler
import logging

logger = logging.getLogger(__name__)


@shared_task
def scrape_target(target_id):
    """指定されたターゲットをスクレイピングするタスク"""
    try:
        target = ScrapingTarget.objects.get(id=target_id, is_active=True)
        
        # ジョブレコードを作成
        job = ScrapingJob.objects.create(
            target=target,
            status='running',
            started_at=timezone.now()
        )
        
        # スクレイピング方法を判定
        use_selenium = detect_scraping_method(target.url)
        
        # スクレイピング実行
        with ScrapingEngine(use_selenium=use_selenium) as scraper:
            if target.enable_crawling:
                # クロールモード
                logger.info(f"Starting crawl mode for {target.name}")
                crawler = WebCrawler(target, scraper)
                results = crawler.crawl()
            else:
                # 単一ページモード
                logger.info(f"Starting single page mode for {target.name}")
                results = scraper.scrape(target.url, target.css_selector)
                # 単一ページの場合はdepthを0に設定
                for result in results:
                    result['depth'] = 0
            
            # データベースに保存
            scraped_items = []
            for result in results:
                scraped_data = ScrapedData(
                    target=target,
                    title=result['title'],
                    content=result['content'],
                    url=result.get('url', target.url),
                    depth=result.get('depth', 0),
                    scraped_at=timezone.now()
                )
                scraped_items.append(scraped_data)
            
            # バルクインサート
            ScrapedData.objects.bulk_create(scraped_items)
            
            # ジョブ完了
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.items_scraped = len(scraped_items)
            job.save()
            
            mode = "crawl" if target.enable_crawling else "single page"
            logger.info(f"Scraping completed for {target.name} ({mode}): {len(scraped_items)} items")
            return f"Successfully scraped {len(scraped_items)} items from {target.name} ({mode})"
            
    except ScrapingTarget.DoesNotExist:
        logger.error(f"ScrapingTarget with id {target_id} not found")
        return f"Target {target_id} not found"
        
    except Exception as e:
        logger.error(f"Scraping failed for target {target_id}: {str(e)}")
        
        # ジョブを失敗として記録
        if 'job' in locals():
            job.status = 'failed'
            job.completed_at = timezone.now()
            job.error_message = str(e)
            job.save()
        
        raise


@shared_task
def scrape_all_active_targets():
    """全ての有効なターゲットをスクレイピング"""
    active_targets = ScrapingTarget.objects.filter(is_active=True)
    
    results = []
    for target in active_targets:
        result = scrape_target.delay(target.id)
        results.append(f"Started scraping job for {target.name}: {result.id}")
    
    return results


@shared_task
def cleanup_old_data(days=30):
    """古いスクレイピングデータをクリーンアップ"""
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # 古いスクレイピングデータを削除
    old_data = ScrapedData.objects.filter(scraped_at__lt=cutoff_date)
    count = old_data.count()
    old_data.delete()
    
    # 古いジョブレコードも削除
    old_jobs = ScrapingJob.objects.filter(started_at__lt=cutoff_date)
    job_count = old_jobs.count()
    old_jobs.delete()
    
    logger.info(f"Cleaned up {count} old scraped data items and {job_count} old jobs")
    return f"Cleaned up {count} items and {job_count} jobs older than {days} days" 