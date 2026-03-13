"""
Price Monitor - Core module
Track product prices and detect changes
"""
import json
import sqlite3
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import time
import schedule

from scraper import ProductScraper
from notifier import PriceNotifier


@dataclass
class Product:
    """Product data model"""
    id: int
    name: str
    url: str
    current_price: Optional[float] = None
    previous_price: Optional[float] = None
    currency: str = 'USD'
    last_checked: Optional[str] = None
    image_url: Optional[str] = None
    
    def price_dropped(self) -> bool:
        """Check if price decreased"""
        if self.previous_price is None or self.current_price is None:
            return False
        return self.current_price < self.previous_price
    
    def price_change_percent(self) -> float:
        """Calculate price change percentage"""
        if self.previous_price is None or self.previous_price == 0:
            return 0.0
        return ((self.current_price - self.previous_price) / self.previous_price) * 100


class PriceDatabase:
    """SQLite database for price history"""
    
    def __init__(self, db_path: str = 'prices.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    current_price REAL,
                    previous_price REAL,
                    currency TEXT DEFAULT 'USD',
                    last_checked TEXT,
                    image_url TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    price REAL,
                    checked_at TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            conn.commit()
    
    def add_product(self, name: str, url: str) -> int:
        """Add new product to track"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'INSERT OR IGNORE INTO products (name, url) VALUES (?, ?)',
                (name, url)
            )
            conn.commit()
            
            # Return product ID
            result = conn.execute(
                'SELECT id FROM products WHERE url = ?', (url,)
            ).fetchone()
            return result[0] if result else cursor.lastrowid
    
    def get_all_products(self) -> List[Product]:
        """Get all tracked products"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM products').fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    url=row['url'],
                    current_price=row['current_price'],
                    previous_price=row['previous_price'],
                    currency=row['currency'] or 'USD',
                    last_checked=row['last_checked'],
                    image_url=row['image_url']
                )
                for row in rows
            ]
    
    def update_price(self, product_id: int, new_price: float):
        """Update product price and save to history"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get current price
            row = conn.execute(
                'SELECT current_price FROM products WHERE id = ?',
                (product_id,)
            ).fetchone()
            
            previous_price = row[0] if row else None
            
            # Update product
            conn.execute('''
                UPDATE products 
                SET previous_price = ?, current_price = ?, last_checked = ?
                WHERE id = ?
            ''', (previous_price, new_price, now, product_id))
            
            # Add to history
            conn.execute('''
                INSERT INTO price_history (product_id, price, checked_at)
                VALUES (?, ?, ?)
            ''', (product_id, new_price, now))
            
            conn.commit()
    
    def get_price_history(self, product_id: int) -> List[Dict]:
        """Get price history for a product"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('''
                SELECT price, checked_at 
                FROM price_history 
                WHERE product_id = ?
                ORDER BY checked_at
            ''', (product_id,)).fetchall()
            
            return [
                {'price': row['price'], 'date': row['checked_at']}
                for row in rows
            ]


class PriceMonitor:
    """Main price monitoring class"""
    
    def __init__(self):
        self.db = PriceDatabase()
        self.scraper = ProductScraper()
        self.notifier = PriceNotifier()
    
    def add_product(self, name: str, url: str) -> int:
        """Add a product to monitor"""
        product_id = self.db.add_product(name, url)
        print(f"✅ Added: {name}")
        return product_id
    
    def check_prices(self) -> List[Product]:
        """Check all product prices"""
        products = self.db.get_all_products()
        updated = []
        
        for product in products:
            print(f"🔍 Checking: {product.name}")
            
            try:
                price_info = self.scraper.get_price(product.url)
                
                if price_info and price_info.get('price'):
                    new_price = price_info['price']
                    self.db.update_price(product.id, new_price)
                    
                    # Reload product with updated prices
                    product.previous_price = product.current_price
                    product.current_price = new_price
                    
                    print(f"   💰 Price: ${new_price:.2f}")
                    
                    # Check for price drop
                    if product.price_dropped():
                        change = abs(product.price_change_percent())
                        print(f"   🎉 Price dropped {change:.1f}%!")
                        self.notifier.send_price_alert(product)
                    
                    updated.append(product)
                else:
                    print(f"   ⚠️ Could not extract price")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(2)  # Rate limiting
        
        return updated
    
    def run_scheduled(self, interval_minutes: int = 60):
        """Run monitoring on schedule"""
        print(f"⏰ Starting scheduled monitoring (every {interval_minutes} minutes)")
        
        schedule.every(interval_minutes).minutes.do(self.check_prices)
        
        # Run immediately
        self.check_prices()
        
        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Price Monitor')
    parser.add_argument('--add', metavar='URL', help='Add product URL to track')
    parser.add_argument('--name', help='Product name')
    parser.add_argument('--check', action='store_true', help='Check prices once')
    parser.add_argument('--monitor', action='store_true', help='Start scheduled monitoring')
    parser.add_argument('--interval', type=int, default=60, help='Check interval (minutes)')
    parser.add_argument('--list', action='store_true', help='List tracked products')
    
    args = parser.parse_args()
    
    monitor = PriceMonitor()
    
    if args.add:
        name = args.name or "Untitled Product"
        monitor.add_product(name, args.add)
    
    elif args.check:
        monitor.check_prices()
    
    elif args.monitor:
        monitor.run_scheduled(args.interval)
    
    elif args.list:
        products = monitor.db.get_all_products()
        print(f"\n📦 Tracking {len(products)} products:\n")
        for p in products:
            price = f"${p.current_price:.2f}" if p.current_price else "N/A"
            print(f"  • {p.name}: {price}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
