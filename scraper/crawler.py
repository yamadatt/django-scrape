import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
from collections import deque
import re

logger = logging.getLogger(__name__)


class WebCrawler:
    """Webサイト全体をクロールするクラス"""
    
    def __init__(self, target, scraping_engine):
        self.target = target
        self.scraping_engine = scraping_engine
        self.visited_urls = set()
        self.url_queue = deque()
        self.scraped_data = []
        
        # 設定
        self.max_depth = target.max_depth
        self.max_pages = target.max_pages
        self.link_selector = target.link_selector
        self.allowed_domains = self._parse_allowed_domains()
        self.exclude_patterns = self._parse_exclude_patterns()
        
        # 統計
        self.pages_crawled = 0
        
    def _parse_allowed_domains(self):
        """許可ドメインを解析"""
        if self.target.allowed_domains.strip():
            domains = [d.strip() for d in self.target.allowed_domains.split('\n') if d.strip()]
            return domains
        else:
            # デフォルトは開始URLと同じドメイン
            parsed = urlparse(self.target.url)
            return [parsed.netloc]
    
    def _parse_exclude_patterns(self):
        """除外パターンを解析"""
        if self.target.exclude_patterns.strip():
            patterns = [p.strip() for p in self.target.exclude_patterns.split('\n') if p.strip()]
            return [re.compile(p) for p in patterns]
        return []
    
    def _is_valid_url(self, url):
        """URLが有効かチェック"""
        try:
            parsed = urlparse(url)
            
            # スキームチェック
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # ドメインチェック
            if parsed.netloc not in self.allowed_domains:
                return False
            
            # 除外パターンチェック
            for pattern in self.exclude_patterns:
                if pattern.search(url):
                    return False
            
            # 既に訪問済みかチェック
            if url in self.visited_urls:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_links(self, html_content, base_url):
        """HTMLからリンクを抽出"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.select(self.link_selector)
            
            extracted_urls = []
            for link in links:
                href = link.get('href')
                if href:
                    # 相対URLを絶対URLに変換
                    absolute_url = urljoin(base_url, href)
                    
                    # フラグメント（#以降）を除去
                    if '#' in absolute_url:
                        absolute_url = absolute_url.split('#')[0]
                    
                    if self._is_valid_url(absolute_url):
                        extracted_urls.append(absolute_url)
            
            return extracted_urls
            
        except Exception as e:
            logger.error(f"Link extraction error: {e}")
            return []
    
    def _scrape_page(self, url, depth):
        """単一ページをスクレイピング"""
        try:
            # スクレイピング実行
            results = self.scraping_engine.scrape(url, self.target.css_selector)
            
            # 結果を保存
            for result in results:
                scraped_item = {
                    'title': result['title'],
                    'content': result['content'],
                    'url': url,
                    'depth': depth
                }
                self.scraped_data.append(scraped_item)
            
            # HTMLを取得してリンクを抽出（次の深度用）
            if depth < self.max_depth:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    links = self._extract_links(response.text, url)
                    
                    # 新しいリンクをキューに追加
                    for link in links:
                        if link not in self.visited_urls and self.pages_crawled < self.max_pages:
                            self.url_queue.append((link, depth + 1))
                    
                except Exception as e:
                    logger.warning(f"Link extraction failed for {url}: {e}")
            
            return len(results)
            
        except Exception as e:
            logger.error(f"Page scraping error for {url}: {e}")
            return 0
    
    def crawl(self):
        """クロール実行"""
        logger.info(f"Starting crawl for {self.target.name}")
        logger.info(f"Max depth: {self.max_depth}, Max pages: {self.max_pages}")
        
        # 開始URLをキューに追加
        self.url_queue.append((self.target.url, 0))
        
        while self.url_queue and self.pages_crawled < self.max_pages:
            url, depth = self.url_queue.popleft()
            
            if url in self.visited_urls:
                continue
            
            logger.info(f"Crawling: {url} (depth: {depth})")
            
            # ページをスクレイピング
            items_count = self._scrape_page(url, depth)
            
            # 訪問済みに追加
            self.visited_urls.add(url)
            self.pages_crawled += 1
            
            logger.info(f"Scraped {items_count} items from {url}")
            
            # レート制限（サーバーに負荷をかけないよう）
            time.sleep(1)
        
        logger.info(f"Crawl completed. Pages: {self.pages_crawled}, Items: {len(self.scraped_data)}")
        return self.scraped_data