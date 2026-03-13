# Price Monitoring Dashboard

Automated price tracking system with notifications. Monitor product prices and get alerts when prices drop.

## 🌟 Features

- ✅ Track multiple products automatically
- ✅ Price drop alerts via email/webhook
- ✅ Historical price data storage
- ✅ Cron-based scheduled monitoring
- ✅ Simple web dashboard (Streamlit)
- ✅ Export price history to CSV/Excel
- ✅ Support for multiple e-commerce sites

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Add a product to track
```bash
python price_monitor.py --add "https://example.com/product" --name "Product Name"
```

### Check prices once
```bash
python price_monitor.py --check
```

### Start monitoring (runs continuously)
```bash
python price_monitor.py --monitor --interval 3600  # Check every hour
```

### Launch dashboard
```bash
streamlit run dashboard.py
```

## 📊 Dashboard Features

- Price history charts
- Current prices table
- Price change alerts
- Export data

## 🔧 Configuration

Create `.env` file:
```
EMAIL_SMTP=smtp.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
WEBHOOK_URL=https://hooks.slack.com/your/webhook
```

## 📁 Files

| File | Description |
|------|-------------|
| `price_monitor.py` | Core monitoring logic |
| `scraper.py` | Product page scrapers |
| `notifier.py` | Email/webhook notifications |
| `database.py` | SQLite data storage |
| `dashboard.py` | Streamlit web interface |

## License

MIT
