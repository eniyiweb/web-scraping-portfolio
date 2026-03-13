# News & Content Scraper

Extract articles, headlines, and content from news websites and blogs.

## Features

- ✅ Article extraction with title, content, author, date
- ✅ Category-based filtering
- ✅ Keyword search within articles
- ✅ Sentiment analysis ready
- ✅ RSS feed support
- ✅ Duplicate detection
- ✅ Auto-throttling

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Scrape latest news
python main.py --url "https://news-site.com" --limit 50

# Filter by category
python main.py --url "https://blog.com" --category "technology" --days 7

# Full content extraction
python main.py --url "https://news.com" --full-content --output articles.json
```

## Example Output

```json
{
  "articles": [
    {
      "title": "New AI Breakthrough Announced",
      "author": "John Smith",
      "published_date": "2024-01-15",
      "category": "Technology",
      "summary": "Researchers announced...",
      "full_content": "Full article text here...",
      "url": "https://news.com/article/123",
      "scraped_at": "2024-01-15T14:30:00"
    }
  ]
}
```

## Use Cases

- Media monitoring
- Content aggregation
- Sentiment analysis datasets
- Trend tracking
- Competitor analysis

## License

MIT
