import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)


class ScrapingEngine:
    """スクレイピングエンジン"""
    
    def __init__(self, use_selenium=False):
        self.use_selenium = use_selenium
        self.driver = None
        
    def __enter__(self):
        if self.use_selenium:
            self._setup_selenium()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
    
    def _setup_selenium(self):
        """Seleniumドライバーのセットアップ"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # ChromiumDriverを使用（ARM64対応）
        from selenium.webdriver.chrome.service import Service
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(getattr(settings, 'SELENIUM_TIMEOUT', 30))
        
    def scrape_with_requests(self, url, css_selector):
        """requestsとBeautifulSoupを使ったスクレイピング"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.select(css_selector)
            
            results = []
            for element in elements:
                title = element.get_text(strip=True)
                link = element.get('href', '')
                if link and not link.startswith('http'):
                    from urllib.parse import urljoin
                    link = urljoin(url, link)
                
                results.append({
                    'title': title,
                    'content': title,
                    'url': link
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Requests scraping error for {url}: {str(e)}")
            raise
    
    def scrape_with_selenium(self, url, css_selector):
        """Seleniumを使ったスクレイピング"""
        try:
            self.driver.get(url)
            
            # ページの読み込み完了を待つ
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 少し待機（JSの実行時間を考慮）
            time.sleep(2)
            
            elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
            
            results = []
            for element in elements:
                title = element.text.strip()
                link = element.get_attribute('href') or ''
                
                results.append({
                    'title': title,
                    'content': title,
                    'url': link
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Selenium scraping error for {url}: {str(e)}")
            raise
    
    def scrape(self, url, css_selector):
        """スクレイピング実行（メソッドを自動選択）"""
        if self.use_selenium:
            return self.scrape_with_selenium(url, css_selector)
        else:
            return self.scrape_with_requests(url, css_selector)


def detect_scraping_method(url):
    """URLに基づいてスクレイピング方法を判定"""
    # JSが多用されているサイトではSeleniumを使用
    js_heavy_domains = [
        'twitter.com',
        'facebook.com', 
        'instagram.com',
        'linkedin.com',
        'spa-site.com'  # SPAサイトの例
    ]
    
    for domain in js_heavy_domains:
        if domain in url:
            return True
    
    return False 