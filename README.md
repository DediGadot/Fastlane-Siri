# Fast Lane Price Service 🛣️

A simple, reliable serverless service to get the current toll price for Israel's Fast Lane (הנתיב המהיר) with Siri integration.

## Features

- ⚡ **Fast**: 5-minute caching, sub-second responses
- 💰 **Cheap**: Runs on AWS free tier, costs pennies per month
- 🗣️ **Siri Ready**: "Hey Siri, what's the fast lane price?"
- 🏗️ **Serverless**: No servers to maintain, scales automatically
- 🔒 **Reliable**: Error handling, health checks, monitoring

## Quick Start

### Prerequisites

1. **AWS Account** with CLI configured:
   ```bash
   aws configure
   ```

2. **Node.js** (v18+):
   ```bash
   node --version  # Should be 18+
   ```

3. **Python** (3.11):
   ```bash
   python3 --version  # Should be 3.11+
   ```

### Deploy in 2 Minutes

```bash
git clone <this-repo>
cd fastlane
./deploy.sh
```

That's it. The script will:
- Install dependencies
- Deploy to AWS
- Test the endpoint
- Give you the API URL for Siri

## Siri Integration (iPhone)

### Step 1: Create Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **"+"** to create new shortcut
3. Search for **"Get Contents of URL"**
4. Add it and configure:
   - **URL**: `https://YOUR-API-URL/price` (from deployment output)
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

### Alternative Setup (Copy-Paste)

Import this shortcut JSON directly:

```json
{
  "WFWorkflowActions": [
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
      "WFWorkflowActionParameters": {
        "WFHTTPMethod": "GET",
        "WFURL": "YOUR-API-URL/price"
      }
    },
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
      "WFWorkflowActionParameters": {
        "WFDictionaryKey": "text_he"
      }
    },
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.speaktext"
    }
  ]
}
```

Replace `YOUR-API-URL` with your actual endpoint.

## API Reference

### GET /price

Returns current Fast Lane toll price.

**Response:**
```json
{
  "price": 8,
  "cached": false,
  "timestamp": "2025-01-15T10:30:00",
  "text_he": "המחיר בנתיב המהיר כעת: 8 שקלים",
  "text_en": "Fast lane toll price: 8 shekels",
  "currency": "ILS"
}
```

**Fields:**
- `price`: Price in Israeli New Shekels (NIS)
- `cached`: Whether result came from cache
- `timestamp`: When price was fetched
- `text_he`: Ready-to-speak Hebrew text
- `text_en`: Ready-to-speak English text

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00"
}
```

## Architecture

```
iPhone/Siri → API Gateway → Lambda → DynamoDB Cache
                              ↓
                         fastlane.co.il
```

### Components

- **AWS Lambda**: Runs the scraper code
- **API Gateway**: HTTP endpoint for Siri
- **DynamoDB**: 5-minute price cache
- **BeautifulSoup4**: HTML parsing
- **Serverless Framework**: Infrastructure as code

### Cost Estimate

With AWS Free Tier:
- **Lambda**: 1M requests/month FREE
- **API Gateway**: 1M requests/month FREE  
- **DynamoDB**: 25GB storage FREE

**Real cost**: $0.00 for normal usage (few requests per day)

## Development

### Local Testing

Test the scraper locally:

```bash
python3 -c "
import requests
from scraper import extract_price
html = requests.get('https://fastlane.co.il').text
print('Price:', extract_price(html))
"
```

Test Lambda locally:

```bash
serverless invoke local -f getPrice
```

### Project Structure

```
fastlane/
├── handler.py          # Lambda functions
├── scraper.py          # Price extraction logic
├── serverless.yml      # AWS infrastructure
├── requirements.txt    # Python dependencies
├── deploy.sh          # One-click deployment
├── package.json       # Node.js config
└── README.md          # This file
```

### Monitoring

View logs in AWS CloudWatch:

```bash
serverless logs -f getPrice --tail
```

### Environment Variables

- `CACHE_TABLE`: DynamoDB table name (auto-configured)

## Troubleshooting

### "Deployment failed"

1. Check AWS credentials:
   ```bash
   aws sts get-caller-identity
   ```

2. Check AWS permissions (need Lambda, API Gateway, DynamoDB)

3. Try different region:
   ```bash
   ./deploy.sh prod eu-west-1
   ```

### "Siri can't find the price"

1. Test API manually:
   ```bash
   curl https://YOUR-API-URL/price
   ```

2. Check shortcut URL is correct

3. Verify internet connection

### "Price seems wrong"

The service validates prices are between 1-100 NIS. If Fast Lane changes pricing significantly, update `validate_price()` in `scraper.py`.

### Lambda Timeout

Current timeout is 30 seconds. If Fast Lane website is slow:

1. Increase timeout in `serverless.yml`
2. Redeploy: `./deploy.sh`

## Contributing

This is meant to be simple. Pull requests welcome for:

- Bug fixes
- Better error handling  
- Price validation improvements
- Documentation fixes

**Not welcome:**
- Complex features
- Additional dependencies
- Over-engineering

## License

MIT License. Use it, modify it, deploy it.

## Disclaimer

This service scrapes publicly available pricing information from fastlane.co.il. It's provided as-is for educational purposes. The author is not affiliated with Fast Lane or Derech Eretz Ltd.

**Hebrew**: השירות הזה אוסף מידע על מחירים זמינים לציבור מאתר fastlane.co.il. מסופק כפי שהוא למטרות חינוכיות. המחבר אינו קשור לנתיב המהיר או דרך ארץ בע״ם.

---

*Built with ❤️ and frustration with toll road pricing opacity*