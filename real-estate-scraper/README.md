# Real Estate Listings Scraper

Extract property listings from real estate websites with detailed information.

## Features

- ✅ Property details: price, location, size, bedrooms, bathrooms
- ✅ Contact information extraction
- ✅ Image URLs collection
- ✅ Geolocation data (when available)
- ✅ Filter by price range, location, property type
- ✅ Scheduled scraping with cron

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Scrape all listings from a city
python main.py --city "istanbul" --output listings.json

# With filters
python main.py --city "ankara" --min-price 500000 --max-price 1000000 --type "apartment"

# Export to Excel
python main.py --url "https://emlak-site.com/listings" --format excel
```

## Example Output

```json
{
  "listings": [
    {
      "title": "3+1 Modern Apartment in Kadıköy",
      "price": "2,500,000 TL",
      "location": "Kadıköy, Istanbul",
      "bedrooms": 3,
      "bathrooms": 1,
      "size_sqm": 120,
      "property_type": "Apartment",
      "contact_phone": "+90 555 123 4567",
      "images": ["https://...", "https://..."],
      "listing_url": "https://...",
      "scraped_at": "2024-01-15T10:30:00"
    }
  ]
}
```

## Supported Platforms

- Sahibinden.com
- Hepsiemlak
- Zingat
- Any custom real estate website

## License

MIT
