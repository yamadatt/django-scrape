# 🕷️ Django Webスクレイピングアプリケーション

Django + Celery + PostgreSQL + Redis を使用した本格的なWebスクレイピングシステム

## 📋 概要

このアプリケーションは、複数のWebサイトから自動的にデータを収集・管理できる包括的なスクレイピングシステムです。単一ページのスクレイピングから、サイト全体のクロールまで対応しています。

## 🎯 主な機能

### **スクレイピング機能**
- 🕷️ **多様なスクレイピング手法**: requests + BeautifulSoup および Selenium の両方をサポート
- 🕸️ **サイト全体クロール**: 指定したサイトの全ページを巡回
- 🎯 **インテリジェント判定**: URLに基づいて最適なスクレイピング方法を自動選択
- ⏱️ **レート制限**: サーバー負荷を考慮した適切な間隔制御（1秒間隔）
- 🎛️ **詳細設定**: 最大深度、最大ページ数、許可ドメイン、除外パターンの設定

### **システム機能**
- 🔄 **非同期処理**: Celeryを使用したバックグラウンドタスク処理
- 📊 **Webダッシュボード**: 直感的なWeb UIでスクレイピングを管理
- 📈 **ジョブ管理**: スクレイピングタスクのリアルタイムステータス監視
- 🗄️ **データ管理**: PostgreSQLによる堅牢なデータ保存・検索
- 🎛️ **管理画面**: Django Adminによる詳細設定
- 🐳 **Docker対応**: ワンクリックで環境構築
- 🧹 **自動クリーンアップ**: 古いデータの自動削除機能

## 🏗️ 技術構成

| 技術 | 用途 | バージョン |
|------|------|-----------|
| **Django** | Webフレームワーク | 4.2.7 |
| **PostgreSQL** | データベース | 15 |
| **Celery** | バックグラウンド処理 | 5.3.4 |
| **Redis** | メッセージブローカー・キャッシュ | 7-alpine |
| **Selenium** | JavaScript対応スクレイピング | 4.15.2 |
| **BeautifulSoup** | HTML解析 | 4.12.2 |
| **Bootstrap** | フロントエンドUI | 5.1.3 |
| **Docker** | コンテナ環境 | - |

## ✨ 特徴

### **2つのスクレイピングモード**
1. **単一ページモード**: 指定したページのみをスクレイピング
2. **サイト全体クロールモード**: サイト全体を巡回してデータ収集
   - 最大深度設定（デフォルト: 2階層）
   - 最大ページ数制限（デフォルト: 50ページ）
   - 許可ドメイン設定
   - 除外URLパターン設定

### **高度なクロール機能**
- **深度制御**: 指定した階層まで自動巡回
- **ドメイン制限**: 許可されたドメインのみクロール
- **除外パターン**: 不要なURLを正規表現で除外
- **レート制限**: サーバー負荷軽減のための1秒間隔制御

## 🎯 活用例・設定例

### **ニュースサイトのクロール**
```
サイト名: 技術ニュースサイト
URL: https://example-tech-news.com
CSSセレクタ: h1, h2, .article-title
サイト全体クロール: ✅
最大深度: 2
最大ページ数: 50
除外パターン:
#
.pdf
/tag/
/category/
```

### **企業サイトの監視**
```
サイト名: 競合企業サイト
URL: https://competitor.com
CSSセレクタ: h1, h2, .news-title
サイト全体クロール: ✅
最大深度: 2
最大ページ数: 30
除外パターン:
#
.pdf
/contact
/admin
/login
```

### **ブログの全記事収集**
```
サイト名: 技術ブログ
URL: https://tech-blog.example.com
CSSセレクタ: .post-title, .entry-title
サイト全体クロール: ✅
最大深度: 3
最大ページ数: 200
除外パターン:
#
/page/
?page=
.jpg
.png
```

### **ECサイトの商品情報**
```
サイト名: オンラインショップ
URL: https://shop.example.com
CSSセレクタ: .product-title, .price
サイト全体クロール: ✅
最大深度: 2
最大ページ数: 100
除外パターン:
#
/cart
/checkout
/account
.pdf
```
- **ドメイン制限**: 同一ドメインまたは指定ドメインのみ
- **除外パターン**: 不要なURL（画像、PDF等）を除外
- **重複除去**: 同じページの重複アクセスを防止
- **フロントエンド**: Bootstrap 5

## クイックスタート

### 1. リポジトリをクローン

\`\`\`bash
git clone <このリポジトリ>
cd django-scraping-app
\`\`\`

### 2. Docker Composeでアプリケーションを起動

\`\`\`bash
docker-compose up --build
\`\`\`

### 3. データベースマイグレーション

\`\`\`bash
docker-compose exec web python manage.py migrate
\`\`\`

### 4. スーパーユーザーを作成

\`\`\`bash
docker-compose exec web python manage.py createsuperuser
\`\`\`

### 5. アプリケーションにアクセス

- **Webアプリケーション**: http://localhost:8000
- **Django管理画面**: http://localhost:8000/admin
- **ダッシュボード**: http://localhost:8000/ (統計情報とクイックアクション)
- **ターゲット管理**: http://localhost:8000/targets/
- **データ一覧**: http://localhost:8000/data/
- **ジョブ履歴**: http://localhost:8000/jobs/

## 📖 使用方法

### 1. スクレイピング対象の登録

#### **基本設定**
1. Django管理画面 (http://localhost:8000/admin) にアクセス
2. 「スクレイピング対象」セクションで新規作成
3. 基本情報を入力：
   - **サイト名**: 分かりやすい名前
   - **URL**: スクレイピング対象のURL
   - **CSSセレクタ**: 取得したい要素のCSSセレクタ
   - **有効**: チェックを入れる

#### **🕸️ サイト全体クロール設定（NEW!）**
サイト全体をクロールする場合は、以下の設定を追加：

- **✅ サイト全体クロール**: チェックを入れる
- **📊 最大深度**: クロールする階層数（推奨: 2-3）
- **📄 最大ページ数**: 取得する最大ページ数（推奨: 10-100）
- **🔗 リンクセレクタ**: `a[href]`（デフォルト）
- **🌐 許可ドメイン**: 空白（同一ドメインのみ）または指定ドメイン
- **🚫 除外パターン**: 除外するURLパターン（改行区切り）

#### **除外パターンの例**
```
#
.pdf
.jpg
.png
/admin
/login
/contact
?page=
```

### 2. スクレイピングの実行

#### **Webインターフェースから**
- **個別実行**: ダッシュボードから特定のサイトの「スクレイピング開始」ボタンをクリック
- **一括実行**: ダッシュボードの「全サイトスクレイピング開始」ボタンをクリック

#### **コマンドラインから**
```bash
# 個別実行
docker-compose exec web python manage.py shell -c "
from scraper.tasks import scrape_target
result = scrape_target.delay(対象ID)
print(f'タスクID: {result.id}')
"

# 全対象実行
docker-compose exec web python manage.py shell -c "
from scraper.tasks import scrape_all_active_targets
result = scrape_all_active_targets.delay()
"
```

### 3. 結果の確認

#### **Webダッシュボードで確認**
- **ダッシュボード** (`/`): 統計情報と最新データ
- **データ一覧** (`/data/`): 取得したデータの詳細
- **ジョブ一覧** (`/jobs/`): 実行履歴とステータス

#### **管理画面で確認**
- **スクレイピングデータ**: 取得したデータの詳細管理
- **スクレイピングジョブ**: ジョブの実行状況

- **ダッシュボード**: 統計情報と最新データの概要
- **スクレイピングデータ**: 取得したデータの一覧
- **ジョブ一覧**: 実行履歴とステータス

## 設定例

### ニュースサイトの見出し取得

\`\`\`
サイト名: サンプルニュース
URL: https://example-news.com
CSSセレクタ: .news-title h2 a
\`\`\`

### ブログ記事のタイトル取得

\`\`\`
サイト名: テックブログ
URL: https://tech-blog.com
CSSセレクタ: article h1.post-title
\`\`\`

## アーキテクチャ

### サービス構成

- **web**: Djangoアプリケーション
- **db**: PostgreSQLデータベース
- **redis**: Celeryブローカー
- **celery**: バックグラウンドワーカー

### データモデル

1. **ScrapingTarget**: スクレイピング対象サイトの設定
   - 基本設定: サイト名、URL、CSSセレクタ
   - クロール設定: 最大深度、最大ページ数、リンクセレクタ、許可ドメイン、除外パターン
2. **ScrapedData**: 取得したデータ
   - データ: タイトル、内容、URL、クロール深度、取得日時
3. **ScrapingJob**: ジョブ実行履歴
   - ステータス: 待機中、実行中、完了、失敗
   - 統計: 開始・完了日時、取得件数、エラーメッセージ

## 開発

### ローカル開発環境

\`\`\`bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# パッケージインストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env

# データベースマイグレーション
python manage.py migrate

# 開発サーバー起動
python manage.py runserver
\`\`\`

### Celeryワーカー起動（開発時）

\`\`\`bash
celery -A scraping_project worker --loglevel=info
\`\`\`

## カスタマイズ

### 新しいスクレイピングロジックの追加

\`scraper/scraping_utils.py\` の \`ScrapingEngine\` クラスを拡張することで、
独自のスクレイピングロジックを追加できます。

### 定期実行の設定

Celery Beatを使用して定期的なスクレイピングを設定できます：

\`\`\`python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'scrape-all-sites': {
        'task': 'scraper.tasks.scrape_all_active_targets',
        'schedule': crontab(hour=0, minute=0),  # 毎日午前0時
    },
}
\`\`\`

## トラブルシューティング

### よくある問題

1. **ChromeDriverエラー**: Dockerコンテナ内でSeleniumが動作しない
   - 解決: Dockerfileで適切なChromeとChromeDriverがインストールされていることを確認

2. **メモリ不足**: 大量のデータをスクレイピング時
   - 解決: \`ScrapedData.objects.bulk_create()\` でバッチ処理を使用

3. **Rate limiting**: サイトからのアクセス制限
   - 解決: \`time.sleep()\` でリクエスト間隔を調整

### ログの確認

\`\`\`bash
# アプリケーションログ
docker-compose logs web

# Celeryワーカーログ
docker-compose logs celery

# すべてのログ
docker-compose logs
\`\`\`

## ライセンス

MIT License

## 貢献

プルリクエストやIssueを歓迎します。開発に参加いただく場合は、
まずIssueを作成して議論してください。

## ⚠️ 注意事項・ベストプラクティス

### **法的・倫理的配慮**
- 📋 対象サイトの**利用規約**と**robots.txt**を必ず確認
- 🤝 **著作権**と**プライバシー**を尊重
- 📧 必要に応じてサイト運営者に**事前連絡**

### **技術的配慮**
- ⏱️ **レート制限**: 1秒間隔でアクセス（デフォルト）
- 📊 **適切な制限値**: 大きすぎる深度・ページ数は避ける
- 🚫 **除外設定**: 画像、PDF、管理画面等を除外
- 🔄 **定期的な監視**: ジョブの実行状況を確認

### **セキュリティ**
- 🔐 本番環境では必ず`.env`ファイルの`SECRET_KEY`を変更
- 🌐 全IPアクセス許可は開発環境のみ使用
- 🛡️ 適切なファイアウォール設定

## 🔧 トラブルシューティング

### **よくある問題と解決方法**

#### **1. ポート競合エラー**
```bash
# エラー: port 5432 already in use
# 解決: docker-compose.ymlのポート設定を変更
ports:
  - "5433:5432"  # ホストポートを変更
```

#### **2. 文字数制限エラー**
```bash
# エラー: value too long for type character varying(500)
# 解決: 既に対応済み（title: 2000文字、url: 500文字）
```

#### **3. クロール機能が動作しない**
```bash
# 確認事項:
# 1. enable_crawling = True に設定されているか
# 2. max_depth, max_pages が適切な値か
# 3. 除外パターンが厳しすぎないか
```

#### **4. ログの確認方法**
```bash
# 全体のログ
docker-compose logs

# 特定のサービスのログ
docker-compose logs web
docker-compose logs celery

# リアルタイムでログを監視
docker-compose logs -f celery
```

## 🚀 高度な使用方法

### **定期実行の設定（Celery Beat）**
```python
# settings.py に追加
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'daily-scraping': {
        'task': 'scraper.tasks.scrape_all_active_targets',
        'schedule': crontab(hour=2, minute=0),  # 毎日午前2時
    },
}
```

### **カスタムスクレイピングタスクの作成**
```python
# scraper/tasks.py に追加
@shared_task
def custom_scraping_task():
    # カスタムロジックを実装
    pass
```

## 🤝 コントリビューション

プルリクエストやIssueを歓迎します！開発に参加いただく場合は：

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**🎉 これで包括的なWebスクレイピングシステムの準備が完了です！**

**主な機能:**
- ✅ 単一ページ・サイト全体クロール対応
- ✅ Django + Celery + PostgreSQL + Redis
- ✅ 美しいWebUI + 管理画面
- ✅ Docker完全対応
- ✅ 詳細なドキュメント

**何か質問や追加したい機能があれば、お気軽にお知らせください！** 