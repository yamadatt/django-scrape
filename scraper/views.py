from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ScrapingTarget, ScrapedData, ScrapingJob
from .tasks import scrape_target, scrape_all_active_targets


def dashboard(request):
    """ダッシュボード画面"""
    targets = ScrapingTarget.objects.filter(is_active=True)
    recent_jobs = ScrapingJob.objects.all()[:10]
    recent_data = ScrapedData.objects.all()[:10]
    
    # 統計情報
    total_targets = targets.count()
    total_scraped = ScrapedData.objects.count()
    running_jobs = ScrapingJob.objects.filter(status='running').count()
    
    context = {
        'targets': targets,
        'recent_jobs': recent_jobs,
        'recent_data': recent_data,
        'total_targets': total_targets,
        'total_scraped': total_scraped,
        'running_jobs': running_jobs,
    }
    return render(request, 'scraper/dashboard.html', context)


def target_list(request):
    """スクレイピング対象一覧"""
    targets = ScrapingTarget.objects.all().order_by('-created_at')
    paginator = Paginator(targets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'scraper/target_list.html', {'page_obj': page_obj})


def scraped_data_list(request):
    """スクレイピングデータ一覧"""
    target_id = request.GET.get('target')
    data = ScrapedData.objects.all()
    
    if target_id:
        data = data.filter(target_id=target_id)
    
    data = data.order_by('-scraped_at')
    paginator = Paginator(data, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    targets = ScrapingTarget.objects.all()
    
    context = {
        'page_obj': page_obj,
        'targets': targets,
        'selected_target': int(target_id) if target_id else None,
    }
    return render(request, 'scraper/data_list.html', context)


def job_list(request):
    """ジョブ一覧"""
    jobs = ScrapingJob.objects.all().order_by('-started_at')
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'scraper/job_list.html', {'page_obj': page_obj})


@require_POST
def start_scraping(request, target_id):
    """個別スクレイピング開始"""
    target = get_object_or_404(ScrapingTarget, id=target_id, is_active=True)
    
    # 既に実行中のジョブがないかチェック
    running_job = ScrapingJob.objects.filter(
        target=target, 
        status='running'
    ).first()
    
    if running_job:
        messages.warning(request, f'{target.name} は既に実行中です。')
    else:
        # タスクをキューに追加
        result = scrape_target.delay(target.id)
        messages.success(request, f'{target.name} のスクレイピングを開始しました。Job ID: {result.id}')
    
    return redirect('scraper:dashboard')


@require_POST 
def start_all_scraping(request):
    """全ターゲットのスクレイピング開始"""
    result = scrape_all_active_targets.delay()
    messages.success(request, f'全ターゲットのスクレイピングを開始しました。Job ID: {result.id}')
    return redirect('scraper:dashboard')


def api_job_status(request, job_id):
    """ジョブステータスAPI"""
    try:
        job = ScrapingJob.objects.get(id=job_id)
        return JsonResponse({
            'status': job.status,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'items_scraped': job.items_scraped,
            'error_message': job.error_message,
        })
    except ScrapingJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404) 