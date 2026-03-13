# E-Commerce Product Scraper

A robust Python scraper for extracting product data from e-commerce websites.

## Features

- ✅ Extract product name, price, rating, reviews, availability
- ✅ Handle pagination automatically
- ✅ Export to CSV, JSON, or Excel
- ✅ Headless browser support (Selenium/Playwright)
- ✅ Rate limiting to avoid detection
- ✅ Proxy support

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python main.py --url "https://example-shop.com/products" --output products.csv

# With pagination
python main.py --url "https://example-shop.com/products" --pages 5 --output products.json

# Custom selectors (for different websites)
python main.py --url "https://shop.com/items" --config config.json
```

## Example Output

```json
{
  "products": [
    {
      "name": "Wireless Headphones Pro",
      "price": "$129.99",
      "rating": 4.5,
      "reviews": 234,
      "availability": "In Stock",
      "url": "https://..."
    }
  ]
}
```

## Supported Sites

Works with any e-commerce platform including:
- Shopify stores
- WooCommerce
- Custom builds
- Amazon (with proper configuration)

## License

MIT
