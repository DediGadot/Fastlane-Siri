# Fast Lane Price Service 🛣️

A simple, reliable **local service** to get the current toll price for Israel's Fast Lane (הנתיב המהיר) with Siri integration.

**NO CLOUD. NO BILLS. YOUR SERVER.**

## Features

- ⚡ **Fast**: 5-minute caching, sub-second responses
- 💰 **Free**: Runs on your hardware, $0/month
- 🗣️ **Siri Ready**: "Hey Siri, what's the fast lane price?"
- 🏠 **Self-Hosted**: Complete control, no external dependencies
- 🔒 **Private**: Your data stays on your server

## Quick Start

```bash
# Start the service
./start.sh

# Test it works
curl http://localhost:8080/price
```

That's it. No AWS account, no cloud setup, just Python.

## Global Access

Your service is running at: `http://YOUR-SERVER-IP:8080/price`

For external access:
1. **Port forwarding**: Forward port 8080 on your router to this server
2. **Firewall**: `sudo ufw allow 8080`
3. **Optional**: Use dynamic DNS service for a stable domain name

## Siri Integration (iPhone)

### Step 1: Create Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **"+"** to create new shortcut
3. Search for **"Get Contents of URL"**
4. Add it and configure:
   - **URL**: `http://YOUR-SERVER-IP:8080/price`
   - **Method**: `GET`

### Step 2: Parse Response

1. Search for **"Get Dictionary from Input"**
2. Add it below the URL action
3. Search for **"Get Dictionary Value"**
4. Add it and set:
   - **Dictionary**: Output from previous step
   - **Key**: `text_he` (for Hebrew) or `text_en` (for English)

### Step 3: Speak Result

1. Search for **"Speak Text"**
2. Add it and connect to dictionary value output
3. Test by tapping ▶️ button

### Step 4: Add Siri Phrase

1. Tap shortcut settings (⚙️)
2. Tap **"Add to Siri"**
3. Record phrase: **"What's the fast lane price?"**
4. Save

## API Reference

### GET /price

Returns current Fast Lane toll price.

**Response:**
```json
{
  "price": 8,
  "cached": true,
  "timestamp": "2025-08-29T10:06:48.272486",
  "text_he": "המחיר בנתיב המהיר: 8 שקלים",
  "text_en": "Fast lane toll price: 8 shekels",
  "currency": "ILS"
}
```

**Fields:**
- `price`: Price in Israeli New Shekels (NIS)
- `cached`: Whether result came from cache (5-minute TTL)
- `timestamp`: When response was generated
- `text_he`: Ready-to-speak Hebrew text
- `text_en`: Ready-to-speak English text

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-29T10:06:48.272486",
  "service": "fastlane-price-local"
}
```

### GET /stats

Request statistics and cache info.

**Response:**
```json
{
  "requests_today": 5,
  "cache": {
    "price": 8,
    "age_seconds": 45,
    "valid": true
  },
  "timestamp": "2025-08-29T10:06:48.272486"
}
```

### GET /

Service information and available endpoints.

## Architecture

```
iPhone/Siri → Your Server:8080 → Flask → SQLite Cache
                                    ↓
                              fastlane.co.il
```

### Components

- **Flask**: Lightweight Python web server
- **Waitress**: Production WSGI server (not Flask dev server)
- **SQLite**: Simple file-based cache database
- **BeautifulSoup4**: HTML parsing for price extraction
- **Requests**: HTTP client for fetching website data

## Project Structure

```
fastlane/
├── app.py                  # Main Flask application
├── run_production.py       # Production server runner
├── scraper.py             # Price extraction logic  
├── start.sh               # One-command startup script
├── requirements_local.txt # Python dependencies
├── README.md              # This file
├── README_LOCAL.md        # Detailed local setup guide
└── venv/                  # Python virtual environment
```

## Management Commands

```bash
# Start service
./start.sh

# Stop service  
kill $(cat service.pid)

# Restart service
./start.sh

# View logs
tail -f service.log

# Check if running
ps -p $(cat service.pid) || echo "Not running"

# Test endpoints
curl localhost:8080/health
curl localhost:8080/price  
curl localhost:8080/stats
```

## Development

### Local Testing

Test the scraper directly:

```bash
source venv/bin/activate
python3 -c "
import requests
from scraper import extract_price
html = requests.get('https://fastlane.co.il').text
print('Price:', extract_price(html), 'NIS')
"
```

Test the Flask app:

```bash
source venv/bin/activate
python3 app.py
# Then in another terminal:
curl localhost:8080/price
```

### Dependencies

Minimal requirements in `requirements_local.txt`:
- `flask==3.0.0` - Web framework
- `waitress==2.1.2` - Production WSGI server  
- `requests==2.31.0` - HTTP client
- `beautifulsoup4==4.12.2` - HTML parser

### Cache Storage

- **Location**: `/tmp/fastlane.db` (SQLite file)
- **TTL**: 5 minutes for price data
- **Tables**: `cache` (price data), `requests` (access logs)

## Troubleshooting

### "Can't access from internet"

1. Check firewall: `sudo ufw status`
2. Check router port forwarding (port 8080 → your server)
3. Check your ISP doesn't block incoming connections
4. Test locally first: `curl localhost:8080/price`

### "Service won't start"

1. Check Python version: `python3 --version` (need 3.7+)
2. Check port availability: `lsof -i :8080`
3. Check logs: `cat service.log`
4. Kill existing process: `pkill -f "python.*app.py"`

### "Price seems wrong"

The service validates prices are between 1-100 NIS. If Fast Lane changes pricing significantly, the validation will reject it. Check logs for "unreasonable price" messages.

### "Siri can't connect"

1. Test API manually: `curl http://YOUR-SERVER-IP:8080/price`
2. Verify iPhone can reach your server IP
3. Check shortcut URL is exactly correct
4. Ensure port 8080 is accessible from internet

## Performance

- **Cold start**: ~2 seconds (scraping website)  
- **Cached response**: ~50ms
- **Memory usage**: ~25MB
- **CPU usage**: Minimal when idle
- **Concurrent requests**: Up to 4 (Waitress default)

## Security

- **Rate limiting**: None (add if needed)
- **Authentication**: None (public price data)
- **HTTPS**: HTTP only (add cert if needed)
- **Firewall**: Recommend restricting to port 8080 only

## Cost

**$0/month** - Runs on your hardware.

Only costs electricity (~1-2 watts continuous).

## Why Local is Better

✅ **Your data** - No cloud provider access  
✅ **Your control** - Modify anything, anytime  
✅ **Always works** - No API rate limits or outages  
✅ **Zero cost** - No monthly cloud bills  
✅ **Simple** - One Python process, one SQLite file  
✅ **Fast** - No network latency to cloud  

## Contributing

Keep it simple. Pull requests welcome for:

- Bug fixes
- Better error handling  
- Price validation improvements
- Documentation improvements

**Not welcome:**
- Complex features
- Additional dependencies
- Cloud integrations
- Over-engineering

## License

MIT License. Use it, modify it, deploy it.

## Disclaimer

This service scrapes publicly available pricing information from fastlane.co.il. It's provided as-is for educational purposes. The author is not affiliated with Fast Lane or Derech Eretz Ltd.

**Hebrew**: השירות הזה אוסף מידע על מחירים זמינים לציבור מאתר fastlane.co.il. מסופק כפי שהוא למטרות חינוכיות. המחבר אינו קשור לנתיב המהיר או דרך ארץ בע״ם.

---

*Built the right way: Simple, local, and reliable.*