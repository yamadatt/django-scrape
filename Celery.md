# Celery について

Celeryは、Pythonで書かれた**分散タスクキュー**システムです。今回のスクレイピングアプリケーションでも重要な役割を果たしています。

## 🔄 Celeryとは

**Celery**は、時間のかかる処理や重い処理を**バックグラウンド**で非同期実行するためのツールです。

### 基本的な仕組み

```
[Webアプリ] → [タスクをキューに追加] → [Celeryワーカーが処理] → [結果を保存]
     ↓                                      ↑
[すぐにレスポンス]                    [バックグラウンドで実行]
```

## 📋 今回のアプリでのCeleryの役割

### 1. **スクレイピングタスクの非同期実行**
```python
# scraper/tasks.py
@shared_task
def scrape_target(target_id):
    """指定されたターゲットをスクレイピングするタスク"""
    # 時間のかかるスクレイピング処理
    target = ScrapingTarget.objects.get(id=target_id)
    # ... スクレイピング実行 ...
```

### 2. **ユーザー体験の向上**
- ユーザーがスクレイピング開始ボタンを押す
- すぐに「開始しました」のメッセージが表示される
- 実際のスクレイピングはバックグラウンドで実行
- ユーザーは他の操作を続けられる

### 3. **システム構成での位置づけ**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Django    │───▶│    Redis    │───▶│   Celery    │
│ Webアプリ    │    │ (ブローカー) │    │ ワーカー     │
└─────────────┘    └─────────────┘    └─────────────┘
        │                                      │
        ▼                                      ▼
┌─────────────┐                    ┌─────────────┐
│ PostgreSQL  │◀───────────────────│スクレイピング│
│ データベース │                    │    実行     │
└─────────────┘                    └─────────────┘
```

## 🛠️ Celeryの主要コンポーネント

### 1. **ブローカー (Broker)**
- **Redis** を使用
- タスクのキューを管理
- DjangoアプリとCeleryワーカー間のメッセージ配信

### 2. **ワーカー (Worker)**
- 実際にタスクを実行するプロセス
- 複数のワーカーを並列実行可能
- ```bash
  celery -A scraping_project worker --loglevel=info
  ```

### 3. **タスク (Task)**
- `@shared_task` デコレータで定義
- 非同期で実行される関数

## 💡 今回のアプリでの具体的な使用例

### タスクの定義
```python
# scraper/tasks.py
@shared_task
def scrape_target(target_id):
    """個別サイトのスクレイピング"""
    # 1. ジョブレコード作成
    # 2. スクレイピング実行
    # 3. データベースに保存
    # 4. ジョブ完了記録

@shared_task
def scrape_all_active_targets():
    """全サイトの一括スクレイピング"""

@shared_task
def cleanup_old_data(days=30):
    """古いデータのクリーンアップ"""
```

### タスクの実行
```python
# scraper/views.py
def start_scraping(request, target_id):
    # タスクをキューに追加（すぐに返る）
    result = scrape_target.delay(target_id)
    messages.success(request, f'スクレイピングを開始しました。Job ID: {result.id}')
    return redirect('scraper:dashboard')
```

## 🎯 Celeryを使う理由

### 1. **レスポンス性の向上**
- スクレイピングは数秒〜数分かかることがある
- ユーザーを待たせない

### 2. **システムの安定性**
- 重い処理でWebサーバーがブロックされない
- 複数のスクレイピングを同時実行可能

### 3. **スケーラビリティ**
- ワーカーを複数台のサーバーに分散可能
- 処理能力を簡単に拡張

### 4. **エラー処理**
- タスクが失敗しても自動リトライ
- エラーログの管理

## 📊 ジョブ管理機能

アプリケーションでは、Celeryタスクの状態を追跡：

```python
class ScrapingJob(models.Model):
    STATUS_CHOICES = [
        ('pending', '待機中'),
        ('running', '実行中'), 
        ('completed', '完了'),
        ('failed', '失敗'),
    ]
    
    target = models.ForeignKey(ScrapingTarget, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    items_scraped = models.IntegerField(default=0)
```

## 🔧 設定例

### Django設定 (settings.py)
```python
# Celery Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
```

### Celery初期化 (scraping_project/celery.py)
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scraping_project.settings')

app = Celery('scraping_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Docker Compose設定
```yaml
celery:
  build: .
  command: celery -A scraping_project worker --loglevel=info
  depends_on:
    - db
    - redis
  environment:
    - DEBUG=1
    - DATABASE_URL=postgresql://scraping_user:scraping_password@db:5432/scraping_db
    - REDIS_URL=redis://redis:6379/0
```

## 🚀 Celeryコマンド

### ワーカー起動
```bash
# 開発環境
celery -A scraping_project worker --loglevel=info

# Docker環境
docker-compose exec celery celery -A scraping_project worker --loglevel=info
```

### タスク監視
```bash
# Celery監視ツール
celery -A scraping_project flower

# ワーカー状態確認
celery -A scraping_project inspect active
```

### 定期実行設定 (Celery Beat)
```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'scrape-all-sites-daily': {
        'task': 'scraper.tasks.scrape_all_active_targets',
        'schedule': crontab(hour=0, minute=0),  # 毎日午前0時
    },
    'cleanup-old-data-weekly': {
        'task': 'scraper.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # 毎週月曜日午前2時
        'args': (30,)  # 30日以上古いデータを削除
    },
}
```

## 🔍 トラブルシューティング

### よくある問題

1. **Celeryワーカーが起動しない**
   ```bash
   # Redis接続確認
   docker-compose logs redis
   
   # Celeryログ確認
   docker-compose logs celery
   ```

2. **タスクが実行されない**
   ```bash
   # ワーカーの状態確認
   celery -A scraping_project inspect active
   
   # キューの確認
   celery -A scraping_project inspect reserved
   ```

3. **メモリ不足**
   ```python
   # タスクでのメモリ効率化
   @shared_task
   def scrape_target(target_id):
       try:
           # 処理
           pass
       finally:
           # リソースのクリーンアップ
           gc.collect()
   ```

## 📈 パフォーマンス最適化

### 1. **並列ワーカー数の調整**
```bash
# CPUコア数に基づいて調整
celery -A scraping_project worker --concurrency=4
```

### 2. **タスクの優先度設定**
```python
@shared_task(priority=1)  # 高優先度
def urgent_scraping_task():
    pass

@shared_task(priority=9)  # 低優先度
def cleanup_task():
    pass
```

### 3. **バッチ処理**
```python
@shared_task
def batch_scrape_targets(target_ids):
    """複数のターゲットをまとめて処理"""
    for target_id in target_ids:
        scrape_single_target(target_id)
```

## 🎉 まとめ

Celeryにより、スクレイピングアプリケーションは：

- ✅ **高性能** - バックグラウンド処理により応答性向上
- ✅ **スケーラブル** - 複数ワーカーでの並列処理
- ✅ **信頼性** - エラー処理とリトライ機能
- ✅ **ユーザーフレンドリー** - 待機時間なしの操作

これらの特徴により、プロダクションレベルのWebスクレイピングシステムが実現されています！ 