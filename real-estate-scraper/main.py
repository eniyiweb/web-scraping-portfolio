import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time

class RealEstateScraper:
    def __init__(self, delay=1):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.delay = delay
        
    def scrape_listings(self, url, pages=1):
        all_listings = []
        
        for page in range(1, pages + 1):
            page_url = f"{url}?page={page}" if '?' not in url else f"{url}&page={page}"
            
            try:
                response = self.session.get(page_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'lxml')
                
                listings = self._parse_listings(soup)
                all_listings.extend(listings)
                
                print(f"✅ Page {page}: {len(listings)} listings found")
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"❌ Page {page} error: {e}")
                continue
                
        return all_listings
    
    def _parse_listings(self, soup):
        listings = []
        
        # Try multiple common selectors for listing cards
        cards = soup.find_all(['article', 'div', 'li'], class_=re.compile('listing|property|estate|ilan', re.I))
        
        for card in cards:
            try:
                listing = {
                    'title': self._extract_text(card, ['h2', 'h3', '.title', '.listing-title']),
                    'price': self._extract_price(card),
                    'location': self._extract_text(card, ['.location', '.address', '.konum']),
                    'bedrooms': self._extract_number(card, ['.bedroom', '.oda', '.room']),
                    'bathrooms': self._extract_number(card, ['.bathroom', '.banyo', '.bath']),
                    'size_sqm': self._extract_size(card),
                    'property_type': self._extract_text(card, ['.type', '.property-type', '.tip']),
                    'listing_url': self._extract_link(card),
                    'scraped_at': datetime.now().isoformat()
                }
                
                if listing['title'] and listing['price']:
                    listings.append(listing)
                    
            except Exception as e:
                continue
                
        return listings
    
    def _extract_text(self, element, selectors):
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        return ''
    
    def _extract_price(self, element):
        price_elem = element.select_one('.price, .fiyat, [class*="price"], [class*="fiyat"]')
        if price_elem:
            return price_elem.get_text(strip=True)
        return ''
    
    def _extract_number(self, element, selectors):
        text = self._extract_text(element, selectors)
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None
    
    def _extract_size(self, element):
        size_elem = element.select_one('.size, .area, .metrekare, .m2, [class*="size"]')
        if size_elem:
            text = size_elem.get_text(strip=True)
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else None
        return None
    
    def _extract_link(self, element):
        link = element.find('a', href=True)
        if link:
            return link['href']
        return ''
    
    def export(self, listings, filename):
        if not listings:
            print("⚠️ No listings found")
            return
            
        if filename.endswith('.json'):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(listings, f, indent=2, ensure_ascii=False)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.DataFrame(listings)
            df.to_excel(filename, index=False)
        else:
            df = pd.DataFrame(listings)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
        print(f"✅ Exported {len(listings)} listings to {filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Real Estate Listings Scraper')
    parser.add_argument('--url', required=True, help='Target URL to scrape')
    parser.add_argument('--pages', type=int, default=1, help='Number of pages')
    parser.add_argument('--output', default='listings.csv', help='Output filename')
    parser.add_argument('--delay', type=float, default=1, help='Delay between requests')
    args = parser.parse_args()
    
    scraper = RealEstateScraper(delay=args.delay)
    listings = scraper.scrape_listings(args.url, args.pages)
    scraper.export(listings, args.output)
