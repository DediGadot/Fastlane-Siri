# Fast Lane Price Service - LOCAL EDITION

No cloud. No monthly bills. Just Python running on YOUR server.

## Quick Start

```bash
# Start the service
./start.sh

# Test it
curl http://localhost:8080/price
```

That's it.

## API Endpoints

- **GET /price** - Current toll price 
- **GET /health** - Health check
- **GET /stats** - Request statistics  
- **GET /** - Service info

## Example Response

```json
{
  "price": 8,
  "cached": true,
  "currency": "ILS",
  "text_he": "המחיר בנתיב המהיר: 8 שקלים",
  "text_en": "Fast lane toll price: 8 shekels",
  "timestamp": "2025-08-29T09:58:24.574364"
}
```

## Siri Integration

1. Open iOS **Shortcuts** app
2. Create new shortcut with:
   - **Get Contents of URL**: `http://YOUR-SERVER-IP:8080/price`
   - **Get Dictionary Value**: key = `text_he` or `text_en` 
   - **Speak Text**: output from above
3. Add Siri phrase: "What's the fast lane price?"

## Global Access

Your service runs on: `http://164.92.163.84:8080/price`

### For internet access:
1. **Port forwarding**: Forward port 8080 on your router
2. **Firewall**: `sudo ufw allow 8080`  
3. **Dynamic DNS**: Use DuckDNS, No-IP, etc. for static domain

## Files

- `app.py` - Flask application (130 lines)
- `run_production.py` - Production server with Waitress
- `start.sh` - One-command startup  
- `scraper.py` - Price extraction (unchanged)
- `requirements_local.txt` - Minimal dependencies

## Management

```bash
# Start
./start.sh

# Stop
kill $(cat service.pid)

# Restart  
./start.sh

# View logs
tail -f service.log

# View stats
curl localhost:8080/stats
```

## Features

✅ **5-minute caching** - Fast responses, reduces load  
✅ **SQLite storage** - Simple file-based database  
✅ **Production WSGI server** - Waitress, not Flask dev server  
✅ **Request logging** - Track usage  
✅ **Health checks** - Monitor service status  
✅ **Zero dependencies** - Just Python + Flask  

## Architecture

```
iPhone/Siri → Your Server:8080 → Flask → SQLite → fastlane.co.il
```

## Cost

**$0/month** - Runs on your hardware

## Why This Is Better

- **Your data** - No cloud provider snooping  
- **Your control** - Change anything, anytime  
- **Always works** - No API rate limits or service outages  
- **Simple** - One Python file, one startup script  

---

Built the Linus way: **Simple. Fast. Works.**