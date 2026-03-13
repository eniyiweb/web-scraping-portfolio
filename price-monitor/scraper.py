"""
Product page scrapers
Extract prices from various e-commerce sites
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from typing import Dict, Optional
import time


class ProductScraper:
    """Universal product scraper with site-specific handlers"""
    
    def __init__(self, use_selenium: bool = False):
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.driver = None
    
    def _init_selenium(self):
        """Initialize Selenium if needed"""
        if self.driver is None:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
    
    def get_price(self, url: str) -> Optional[Dict]:
        """Extract price from product page"""
        try:
            if self.use_selenium or 'amazon' in url.lower():
                return self._scrape_with_selenium(url)
            else:
                return self._scrape_with_requests(url)
        except Exception as e:
            print(f"Scraping error: {e}")
            return None
    
    def _scrape_with_requests(self, url: str) -> Optional[Dict]:
        """Scrape using requests + BeautifulSoup"""
        response = self.session.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Try multiple price selectors
        price_selectors = [
            '.price',
            '.product-price',
            '.current-price',
            '[data-price]',
            '.offer-price',
            '.sale-price'
        ]
        
        price = None
        currency = 'USD'
        
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                price_text = elem.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    break
        
        # Also check meta tags
        if not price:
            meta_price = soup.find('meta', property='product:price:amount')
            if meta_price:
                price = self._parse_price(meta_price.get('content', ''))
        
        return {
            'price': price,
            'currency': currency,
            'url': url
        } if price else None
    
    def _scrape_with_selenium(self, url: str) -> Optional[Dict]:
        """Scrape using Selenium for JavaScript-heavy sites"""
        self._init_selenium()
        
        self.driver.get(url)
        time.sleep(3)  # Wait for JavaScript
        
        # Amazon-specific selectors
        if 'amazon' in url.lower():
            selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '#priceblock_dealprice',
                '#priceblock_ourprice'
            ]
        else:
            selectors = ['.price', '[data-price]', '.current-price']
        
        for selector in selectors:
            try:
                elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                price_text = elem.text
                price = self._parse_price(price_text)
                if price:
                    return {'price': price, 'currency': 'USD', 'url': url}
            except:
                continue
        
        return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        
        # Handle European format (1.234,56)
        if ',' in cleaned and '.' in cleaned:
            if cleaned.rfind(',') > cleaned.rfind('.'):
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except:
            return None
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
