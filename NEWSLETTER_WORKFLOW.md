# Newsletter System - Complete Workflow Documentation

## 📋 COMPLETE WORKFLOW OVERVIEW

### Phase 1: User Subscription (Frontend → Backend → Brevo)

```
1. User clicks "Subscribe to Newsletter" button in sidebar
2. Modal opens with 14 topic chips (8 crypto + 6 NFT)
3. User selects topics (e.g., Bitcoin, Ethereum, NFT Art)
4. User email is pre-filled from Clerk authentication
5. User clicks "Subscribe"
   ↓
6. Frontend sends POST to http://localhost:5000/api/newsletter/subscribe
   {
     "email": "user@example.com",
     "name": "John Doe",
     "topics": ["bitcoin", "ethereum", "nft-art"]
   }
   ↓
7. Backend validates data
8. Backend calls Brevo API to create/update contact
9. Topics saved as attributes in Brevo contact
10. Success message shown to user
```

### Phase 2: News Collection & Newsletter Generation (Scheduled Weekly)

```
1. newsletter_generator.py runs (scheduled via cron/Task Scheduler)
   ↓
2. For each topic (bitcoin, ethereum, altcoins, etc.):
   - Calls search_crypto_news() API
   - Collects latest 3 articles per topic
   - Gets current prices for crypto/NFT topics
   ↓
3. Get all subscribers from Brevo via get_subscribers_by_topics()
   ↓
4. For each subscriber:
   - Filter news by their subscribed topics
   - Generate personalized HTML email
   - Include:
     * Current prices (Bitcoin, Ethereum, NFT floor prices)
     * Latest news articles with links
     * Source and publication date
   ↓
5. Send email via Brevo SMTP API (send_newsletter())
   ↓
6. Log success/failure for each send
```

### Phase 3: Email Delivery (Brevo → User)

```
1. Brevo validates sender email (must be verified)
2. Brevo sends email to subscriber
3. Email includes:
   - Personalized greeting
   - Price updates for relevant assets
   - 3 news articles per subscribed topic
   - Unsubscribe link
4. User receives email in inbox
```

---

## 🔍 DATA SOURCES

### News Content Collection
- **Source**: CoinGecko API via `search_crypto_news()`
- **Endpoint**: https://api.coingecko.com/api/v3/search/trending
- **What it provides**:
  - Latest crypto news articles
  - Article titles, descriptions, URLs
  - Publication dates and sources
  - Trending topics

### Price Data Collection
- **Source**: CoinGecko API via `get_coin_price()` and `get_nft_info()`
- **Endpoints**:
  - `https://api.coingecko.com/api/v3/simple/price` (crypto prices)
  - `https://api.coingecko.com/api/v3/nfts/{id}` (NFT floor prices)
- **What it provides**:
  - Current Bitcoin/Ethereum prices in USD
  - NFT collection floor prices
  - Market data

### Topic Mapping
```python
TOPIC_QUERIES = {
    'bitcoin': 'Bitcoin BTC',
    'ethereum': 'Ethereum ETH',
    'altcoins': 'altcoins cryptocurrency',
    'defi': 'DeFi decentralized finance',
    'trading': 'crypto trading market',
    'mining': 'crypto mining',
    'regulation': 'crypto regulation SEC',
    'market-analysis': 'crypto market analysis',
    'nft-cryptopunks': 'CryptoPunks NFT',
    'nft-bored-ape': 'Bored Ape Yacht Club BAYC',
    'nft-art': 'NFT art digital',
    'nft-gaming': 'NFT gaming play-to-earn',
    'nft-marketplace': 'OpenSea NFT marketplace',
    'nft-metaverse': 'metaverse NFT virtual'
}
```

---

## 📧 NEWSLETTER CONTENT STRUCTURE

### Email Template Sections

1. **Header**
   - Gradient background (#667eea → #764ba2)
   - Title: "🤖 Crypto Chatbot Newsletter"
   - Subtitle: "Your Weekly Digest"

2. **Greeting**
   - Personalized: "Hi {name}! 👋"
   - Introduction text

3. **Topic Sections** (one per subscribed topic)
   - Topic icon and name
   - Current Price Box (if applicable):
     * Large price display
     * Asset symbol
     * "Current Price" or "Floor Price" label
     * Date timestamp
   - News Articles (up to 3):
     * Article title
     * Source name
     * "Read more" link
     * Publication date

4. **Footer**
   - Call to action: "Visit Crypto Chatbot"
   - Copyright notice
   - Unsubscribe link
   - Manage preferences link

---

## 🔄 SCHEDULING OPTIONS

### Option 1: Windows Task Scheduler (Recommended for Windows)

Create a scheduled task to run weekly:

```powershell
# Create a scheduled task for Monday 9 AM
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "c:\Users\Z005652D\Downloads\poc project\newsletter_generator.py --send"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd
Register-ScheduledTask -TaskName "CryptoNewsletter" -Action $action -Trigger $trigger -Settings $settings -Description "Send weekly crypto newsletters"
```

### Option 2: Python Schedule Library

```python
# scheduler.py
import schedule
import time
from newsletter_generator import send_newsletters_to_all_subscribers

# Run every Monday at 9 AM
schedule.every().monday.at("09:00").do(send_newsletters_to_all_subscribers)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### Option 3: Manual Execution

```bash
# Run whenever needed
python newsletter_generator.py --send
```

---

## 🧪 TESTING WORKFLOW

### Test 1: Generate Preview (No Sending)

```bash
python newsletter_generator.py --test
```

**What it does**:
- Collects news for 3 sample topics (Bitcoin, Ethereum, NFT Art)
- Generates HTML newsletter
- Saves to `newsletter_preview.html`
- Opens file in browser to preview

### Test 2: Subscribe a Test User

```bash
python test_newsletter.py
```

**What it does**:
- Sends POST to /api/newsletter/subscribe
- Creates test contact in Brevo
- Validates API response

### Test 3: Send Newsletter to All Subscribers

```bash
python newsletter_generator.py --send
```

**What it does**:
- Collects news for all 14 topics
- Gets all subscribers from Brevo
- Generates personalized newsletters
- Sends via Brevo SMTP
- Displays success/failure report

---

## 📊 DATA FLOW DIAGRAM

```
┌─────────────┐
│   USER      │ Selects topics (Bitcoin, Ethereum, NFT Art)
│ (Frontend)  │
└──────┬──────┘
       │
       │ POST /api/newsletter/subscribe
       │ {email, name, topics: ["bitcoin", "ethereum", "nft-art"]}
       ↓
┌──────────────┐
│ Flask Server │ Validates & processes request
│ (Backend)    │
└──────┬───────┘
       │
       │ API Call: Create/Update Contact
       ↓
┌──────────────┐
│   BREVO      │ Stores:
│  (Database)  │ - email: user@example.com
└──────────────┘ - TOPICS: bitcoin,ethereum,nft-art
                 - SUBSCRIBED_DATE: 2025-12-13

        ... LATER (Weekly Cron Job) ...

┌────────────────────┐
│ newsletter_        │ Runs: python newsletter_generator.py --send
│ generator.py       │
└─────────┬──────────┘
          │
          │ 1. Collect news for each topic
          ↓
┌────────────────────┐
│  CoinGecko API     │ Returns:
│                    │ - News articles (title, url, source)
└─────────┬──────────┘ - Price data (BTC: $42,500)
          │
          │ 2. Get all subscribers
          ↓
┌────────────────────┐
│  BREVO API         │ Returns:
│                    │ [{email: "user@example.com", topics: ["bitcoin", ...]}]
└─────────┬──────────┘
          │
          │ 3. For each subscriber:
          │    - Filter news by their topics
          │    - Generate HTML email
          ↓
┌────────────────────┐
│ generate_          │ Creates personalized HTML with:
│ newsletter_html()  │ - Greeting with name
└─────────┬──────────┘ - Price boxes for crypto/NFT
          │            - 3 news articles per topic
          │
          │ 4. Send via Brevo SMTP
          ↓
┌────────────────────┐
│  BREVO SMTP        │ Sends email to user@example.com
│                    │
└─────────┬──────────┘
          │
          │ Email delivered
          ↓
┌────────────────────┐
│   USER INBOX       │ 📧 "Your Weekly Crypto Digest"
│                    │
└────────────────────┘
```

---

## 🔐 REQUIRED SETUP

### 1. Brevo Account Configuration

✅ **Already configured**:
- API Key: `YOUR_BREVO_API_KEY_HERE`

⚠️ **Still needed**:
- [ ] Verify sender email in Brevo dashboard
- [ ] Update `newsletter_api.py` line 102 with verified sender email
- [ ] Create contact list (optional but recommended)
- [ ] Create contact attributes: TOPICS, SUBSCRIBED_DATE, SOURCE

### 2. Environment Variables

File: `.env`
```
BREVO_API_KEY=YOUR_BREVO_API_KEY_HERE
```

---

## 📝 EXAMPLE NEWSLETTER OUTPUT

**Subject**: Your Weekly Crypto Digest - 3 Topics Update

**Content**:
```html
🤖 Crypto Chatbot Newsletter
Your Weekly Digest

Hi John Doe! 👋

Here's your weekly roundup of the topics you're following:

₿ Bitcoin
┌─────────────────┐
│ Current Price   │
│ $42,350.00      │
│ as of Dec 13    │
└─────────────────┘

📰 Bitcoin Reaches New All-Time High
   📰 CoinDesk
   Read more →

📰 Institutional Investors Pour into BTC
   📰 Bloomberg
   Read more →

Ξ Ethereum
┌─────────────────┐
│ Current Price   │
│ $2,245.00       │
│ as of Dec 13    │
└─────────────────┘

📰 Ethereum 2.0 Upgrade Complete
   📰 Decrypt
   Read more →

🎨 NFT Art
📰 Digital Art Market Explodes in Q4
   📰 The Block
   Read more →

💡 Want to explore more? Visit Crypto Chatbot

You're receiving this because you subscribed to our newsletter.
Crypto Chatbot © 2025 | Powered by AI
Unsubscribe | Manage Preferences
```

---

## ⚡ QUICK START TESTING

### Step 1: Test Newsletter Generation (Preview)

```bash
cd "c:\Users\Z005652D\Downloads\poc project"
python newsletter_generator.py --test
```

This will:
- Collect news for sample topics
- Generate HTML file
- Save as `newsletter_preview.html`
- You can open it in browser to see the design

### Step 2: Subscribe Test User (via API)

```bash
python test_newsletter.py
```

### Step 3: Send Newsletter to Subscribers

```bash
python newsletter_generator.py --send
```

---

## 📈 MONITORING & LOGS

Newsletter generator provides detailed console output:

```
======================================================================
📧 NEWSLETTER GENERATION STARTED
⏰ Time: 2025-12-13 09:00:00
======================================================================

📰 Collecting news for all topics...
   • Fetching news for: ₿ Bitcoin
     ✓ Found 3 articles
   • Fetching news for: Ξ Ethereum
     ✓ Found 3 articles
   [...]

👥 Getting subscribers...
   ✓ Found 5 subscribers

📨 Sending newsletters...

   → Sending to: user1@example.com
      Topics: ₿ Bitcoin, Ξ Ethereum
      ✅ Sent successfully!

   → Sending to: user2@example.com
      Topics: 🎨 NFT Art, 🎮 NFT Gaming
      ✅ Sent successfully!

======================================================================
📊 NEWSLETTER SENDING COMPLETE
   ✅ Successful: 5
   ❌ Failed: 0
   📧 Total: 5
======================================================================
```

---

## 🎯 SUCCESS CRITERIA

Newsletter is working correctly when:

- [x] Users can subscribe via UI modal
- [x] Topics are saved to Brevo contacts
- [ ] Newsletter generator collects news for all 14 topics
- [ ] Personalized HTML emails are generated
- [ ] Emails are sent via Brevo to all subscribers
- [ ] Users receive emails in their inbox
- [ ] Emails contain current prices and news articles
- [ ] Unsubscribe functionality works

---

## 🔧 TROUBLESHOOTING

### Issue: No news articles found
**Solution**: Check CoinGecko API rate limits or try different query terms

### Issue: Email not sending
**Solution**: Verify sender email in Brevo dashboard

### Issue: Subscriber not found
**Solution**: Check Brevo contact list and API key permissions

### Issue: HTML rendering incorrectly
**Solution**: Test with `--test` flag and open preview in browser

