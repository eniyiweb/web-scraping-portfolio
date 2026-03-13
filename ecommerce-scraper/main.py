from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import time
import argparse
from urllib.parse import urljoin

class EcommerceScraper:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def scrape_products(self, url, pages=1):
        products = []
        
        for page in range(1, pages + 1):
            page_url = f"{url}?page={page}" if page > 1 else url
            self.driver.get(page_url)
            time.sleep(2)  # Rate limiting
            
            # Dynamic selectors - can be customized per site
            product_cards = self.driver.find_elements(By.CSS_SELECTOR, '.product-card, .product-item, [data-product]')
            
            for card in product_cards:
                try:
                    product = {
                        'name': self._safe_find(card, ['.product-title', '.product-name', 'h2', 'h3']),
                        'price': self._safe_find(card, ['.price', '.product-price', '[data-price]']),
                        'rating': self._safe_find(card, ['.rating', '.stars'], default='N/A'),
                        'availability': self._safe_find(card, ['.stock', '.availability'], default='Unknown'),
                        'url': self._get_link(card)
                    }
                    products.append(product)
                except Exception as e:
                    continue
                    
        return products
    
    def _safe_find(self, element, selectors, default=''):
        for selector in selectors:
            try:
                found = element.find_element(By.CSS_SELECTOR, selector)
                return found.text.strip()
            except:
                continue
        return default
    
    def _get_link(self, element):
        try:
            link = element.find_element(By.CSS_SELECTOR, 'a')
            return link.get_attribute('href')
        except:
            return ''
    
    def export(self, products, filename):
        if filename.endswith('.json'):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
        else:
            df = pd.DataFrame(products)
            df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Exported {len(products)} products to {filename}")
    
    def close(self):
        self.driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--pages', type=int, default=1, help='Number of pages')
    parser.add_argument('--output', default='products.csv', help='Output file')
    args = parser.parse_args()
    
    scraper = EcommerceScraper()
    try:
        products = scraper.scrape_products(args.url, args.pages)
        scraper.export(products, args.output)
    finally:
        scraper.close()
