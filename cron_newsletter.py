"""
Cron Job Script for Sending Newsletters (Completely Standalone)
Uses direct REST API calls - NO supabase library, NO local imports

VERSION: 2.0 - Standalone (2025-12-23)

Usage:
  python cron_newsletter.py          # Send newsletters
  python cron_newsletter.py --test   # Test without sending
"""
import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("📌 CRON NEWSLETTER v2.0 - STANDALONE VERSION")
print("=" * 60)


# ==============================================
# TOPIC NAMES
# ==============================================

TOPIC_NAMES = {
    'bitcoin': '₿ Bitcoin',
    'ethereum': 'Ξ Ethereum',
    'altcoins': '🪙 Altcoins',
    'defi': '🏦 DeFi',
    'trading': '📈 Trading',
    'mining': '⛏️ Mining',
    'regulation': '⚖️ Regulation',
    'market-analysis': '📊 Market Analysis',
    'nft-cryptopunks': '🎭 CryptoPunks',
    'nft-bored-ape': '🦍 Bored Ape YC',
    'nft-art': '🎨 NFT Art',
    'nft-gaming': '🎮 NFT Gaming',
    'nft-marketplace': '🏪 NFT Marketplaces',
    'nft-metaverse': '🌐 Metaverse'
}


# ==============================================
# SUPABASE REST API
# ==============================================

def get_supabase_headers():
    """Get headers for Supabase REST API"""
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    return {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }


def get_all_active_subscribers():
    """Get all active subscribers using direct REST API"""
    supabase_url = os.getenv('SUPABASE_URL')
    
    url = f"{supabase_url}/rest/v1/newsletter_subscriptions"
    params = {'select': '*', 'is_active': 'eq.true'}
    
    try:
        response = requests.get(url, headers=get_supabase_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching subscribers: {e}")
        return []


# ==============================================
# CRYPTOPANIC NEWS API
# ==============================================

def get_news_for_topic(topic_id, limit=3):
    """Fetch news from CryptoPanic API"""
    api_key = os.getenv('CRYPTOPANIC_API_KEY')
    
    # Map topics to CryptoPanic filters
    filter_map = {
        'bitcoin': 'currencies=BTC',
        'ethereum': 'currencies=ETH',
        'altcoins': 'currencies=SOL,ADA,XRP,DOT',
        'defi': 'currencies=UNI,AAVE,LINK',
        'nft-cryptopunks': 'currencies=ETH',
        'nft-bored-ape': 'currencies=ETH',
        'nft-art': 'currencies=ETH',
        'trading': 'filter=rising',
        'mining': 'filter=important',
        'regulation': 'filter=important',
        'market-analysis': 'filter=bullish,bearish'
    }
    
    filter_param = filter_map.get(topic_id, 'filter=important')
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&{filter_param}&public=true"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])[:limit]
    except Exception as e:
        print(f"   Error fetching news for {topic_id}: {e}")
        return []


# ==============================================
# BREVO EMAIL API
# ==============================================

def send_newsletter_email(email, subject, html_content):
    """Send email using Brevo API"""
    api_key = os.getenv('BREVO_API_KEY')
    
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'api-key': api_key
    }
    
    data = {
        'sender': {'name': 'Crypto Chatbot', 'email': 'newsletter@cryptobot.com'},
        'to': [{'email': email}],
        'subject': subject,
        'htmlContent': html_content
    }
    
    try:
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers=headers,
            json=data
        )
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"   Error sending email: {e}")
        return False


# ==============================================
# HTML GENERATION
# ==============================================

def generate_newsletter_html(name, topics, news_by_topic):
    """Generate HTML email content"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ padding: 30px; }}
            .topic-section {{ margin-bottom: 25px; border-left: 4px solid #667eea; padding-left: 15px; }}
            .topic-title {{ font-size: 18px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
            .news-item {{ background: #f8f9fa; padding: 12px; margin-bottom: 8px; border-radius: 6px; }}
            .news-item h3 {{ margin: 0 0 5px; font-size: 14px; color: #333; }}
            .news-item a {{ color: #667eea; text-decoration: none; font-size: 13px; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Crypto Newsletter</h1>
                <p>Your Weekly Digest - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            <div class="content">
                <p>Hi {name}! 👋 Here's your weekly crypto roundup:</p>
    """
    
    for topic_id in topics:
        topic_name = TOPIC_NAMES.get(topic_id, topic_id)
        articles = news_by_topic.get(topic_id, [])
        
        html += f'<div class="topic-section"><div class="topic-title">{topic_name}</div>'
        
        if articles:
            for article in articles:
                title = article.get('title', 'No title')[:80]
                url = article.get('url', '#')
                source = article.get('source', {}).get('title', '')
                html += f'''
                <div class="news-item">
                    <h3>{title}</h3>
                    <a href="{url}">Read more →</a> {f'<span style="color:#999">({source})</span>' if source else ''}
                </div>'''
        else:
            html += '<p style="color:#999;font-style:italic">No news this week.</p>'
        
        html += '</div>'
    
    html += f"""
            </div>
            <div class="footer">
                <p>Sent by Crypto Chatbot 🤖</p>
                <p>You're receiving this because you subscribed to our newsletter.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


# ==============================================
# LOGGING
# ==============================================

def log(msg):
    """Log with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# ==============================================
# MAIN JOB
# ==============================================

def run_newsletter_job():
    """Main function to run the newsletter job"""
    log("🚀 Starting Newsletter Cron Job")
    log("=" * 50)
    
    # Check environment variables
    required = ['BREVO_API_KEY', 'CRYPTOPANIC_API_KEY', 'SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing = [v for v in required if not os.getenv(v)]
    
    if missing:
        log(f"❌ Missing: {', '.join(missing)}")
        sys.exit(1)
    
    log("✅ All env vars configured")
    
    try:
        # Get subscribers
        log("📧 Fetching subscribers...")
        subscribers = get_all_active_subscribers()
        log(f"   Found {len(subscribers)} active subscribers")
        
        if not subscribers:
            log("⚠️ No subscribers. Exiting.")
            return
        
        # Collect topics
        all_topics = set()
        for sub in subscribers:
            all_topics.update(sub.get('topics', []))
        
        log(f"📋 Fetching news for {len(all_topics)} topics...")
        
        # Fetch news
        news_by_topic = {}
        for topic_id in all_topics:
            log(f"   • {TOPIC_NAMES.get(topic_id, topic_id)}")
            news_by_topic[topic_id] = get_news_for_topic(topic_id, limit=3)
        
        # Send emails
        log("📨 Sending newsletters...")
        success = 0
        failed = 0
        
        for sub in subscribers:
            email = sub.get('user_email')
            name = sub.get('user_name', 'User')
            topics = sub.get('topics', [])
            
            if not email or not topics:
                continue
            
            html = generate_newsletter_html(name, topics, news_by_topic)
            subject = f"Your Weekly Crypto Digest - {len(topics)} Topic{'s' if len(topics) > 1 else ''}"
            
            if send_newsletter_email(email, subject, html):
                log(f"   ✅ {email}")
                success += 1
            else:
                log(f"   ❌ {email}")
                failed += 1
        
        log("=" * 50)
        log(f"📊 Done: {success} sent, {failed} failed")
        
    except Exception as e:
        log(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_test_job():
    """Test without sending"""
    log("🧪 Running Test")
    log("=" * 50)
    
    try:
        subscribers = get_all_active_subscribers()
        log(f"✅ Found {len(subscribers)} subscribers")
        
        for sub in subscribers[:3]:
            log(f"   - {sub.get('user_email')}: {sub.get('topics')}")
        
        log("✅ Test passed")
        
    except Exception as e:
        log(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_test_job()
    else:
        run_newsletter_job()
