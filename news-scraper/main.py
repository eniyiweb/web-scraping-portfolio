import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import argparse
import re
import time
from urllib.parse import urljoin

class NewsScraper:
    def __init__(self, delay=1):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = delay
        self.seen_urls = set()
        
    def scrape_articles(self, url, limit=50, category=None):
        articles = []
        
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find article links
            article_links = self._find_article_links(soup, url, limit)
            
            for link in article_links:
                if link in self.seen_urls:
                    continue
                self.seen_urls.add(link)
                
                try:
                    article = self._scrape_article(link)
                    if article and (not category or category.lower() in article.get('category', '').lower()):
                        articles.append(article)
                        print(f"✅ Scraped: {article['title'][:60]}...")
                    time.sleep(self.delay)
                except Exception as e:
                    print(f"❌ Error scraping {link}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            
        return articles
    
    def _find_article_links(self, soup, base_url, limit):
        links = []
        
        # Common article link selectors
        selectors = [
            'article a', '.news-item a', '.article-link',
            'h2 a', 'h3 a', '.title a', '.headline a'
        ]
        
        for selector in selectors:
            for a in soup.select(selector)[:limit]:
                href = a.get('href', '')
                if href and not href.startswith(('#', 'javascript:')):
                    full_url = urljoin(base_url, href)
                    links.append(full_url)
                    
        return list(set(links))[:limit]
    
    def _scrape_article(self, url):
        response = self.session.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'lxml')
        
        article = {
            'title': self._extract_title(soup),
            'author': self._extract_author(soup),
            'published_date': self._extract_date(soup),
            'category': self._extract_category(soup),
            'summary': self._extract_summary(soup),
            'url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        return article
    
    def _extract_title(self, soup):
        selectors = ['h1', '.article-title', '.post-title', 'title']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ''
    
    def _extract_author(self, soup):
        selectors = ['.author', '.byline', '[rel="author"]', '.writer']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ''
    
    def _extract_date(self, soup):
        selectors = ['time', '.date', '.published', '[datetime]']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                date = elem.get('datetime') or elem.get_text(strip=True)
                return date
        return ''
    
    def _extract_category(self, soup):
        selectors = ['.category', '.tag', '.section']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ''
    
    def _extract_summary(self, soup):
        selectors = ['.summary', '.excerpt', '.lead', 'meta[name="description"]']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if selector == 'meta[name="description"]':
                    return elem.get('content', '')
                return elem.get_text(strip=True)[:300]
        return ''
    
    def export(self, articles, filename):
        if not articles:
            print("⚠️ No articles found")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Exported {len(articles)} articles to {filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='News website URL')
    parser.add_argument('--limit', type=int, default=50, help='Max articles')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--output', default='articles.json', help='Output file')
    parser.add_argument('--delay', type=float, default=1, help='Request delay')
    args = parser.parse_args()
    
    scraper = NewsScraper(delay=args.delay)
    articles = scraper.scrape_articles(args.url, args.limit, args.category)
    scraper.export(articles, args.output)
