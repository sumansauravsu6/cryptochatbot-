"""
Newsletter Generator - Collects news and generates newsletters
This script fetches news for subscribed topics and sends weekly newsletters
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from newsletter_api import get_subscribers_by_topics, send_newsletter
from api_tools import get_coin_price, get_nft_info
from cryptopanic_api import get_news_for_topic

load_dotenv()

# Topic Display Names
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


def collect_news_for_topic(topic_id, limit=3):
    """
    Collect latest news articles for a specific topic using CryptoPanic API
    
    Args:
        topic_id: Topic identifier
        limit: Number of articles to collect
        
    Returns:
        list: List of news articles
    """
    try:
        # Use CryptoPanic API to fetch news
        articles = get_news_for_topic(topic_id, limit)
        return articles
        
    except Exception as e:
        print(f"Error collecting news for {topic_id}: {e}")
        return []


def get_price_data_for_topic(topic_id):
    """
    Get current price data for crypto/NFT topics
    
    Args:
        topic_id: Topic identifier
        
    Returns:
        dict: Price information
    """
    try:
        if topic_id == 'bitcoin':
            price_data = get_coin_price('usd', 'bitcoin')
            return {
                'name': 'Bitcoin',
                'price': f"${price_data.get('bitcoin', {}).get('usd', 0):,.2f}",
                'symbol': 'BTC'
            }
        elif topic_id == 'ethereum':
            price_data = get_coin_price('usd', 'ethereum')
            return {
                'name': 'Ethereum',
                'price': f"${price_data.get('ethereum', {}).get('usd', 0):,.2f}",
                'symbol': 'ETH'
            }
        elif topic_id == 'nft-cryptopunks':
            nft_data = get_nft_info('cryptopunks')
            if 'floor_price' in nft_data:
                return {
                    'name': 'CryptoPunks',
                    'price': f"${nft_data['floor_price'].get('usd', 0):,.0f}",
                    'type': 'Floor Price'
                }
        elif topic_id == 'nft-bored-ape':
            nft_data = get_nft_info('bored-ape-yacht-club')
            if 'floor_price' in nft_data:
                return {
                    'name': 'Bored Ape YC',
                    'price': f"${nft_data['floor_price'].get('usd', 0):,.0f}",
                    'type': 'Floor Price'
                }
    except Exception as e:
        print(f"Error getting price for {topic_id}: {e}")
    
    return None


def generate_newsletter_html(subscriber_name, topics, news_by_topic):
    """
    Generate HTML email content for newsletter
    
    Args:
        subscriber_name: Name of the subscriber
        topics: List of subscribed topics
        news_by_topic: Dictionary of news articles by topic
        
    Returns:
        str: HTML content
    """
    
    # Email header
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .header p {{ margin: 10px 0 0; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .greeting {{ font-size: 18px; margin-bottom: 20px; color: #333; }}
            .topic-section {{ margin-bottom: 30px; border-left: 4px solid #667eea; padding-left: 15px; }}
            .topic-title {{ font-size: 20px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
            .price-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; }}
            .price-box .price {{ font-size: 24px; font-weight: bold; color: #10a37f; }}
            .news-item {{ background: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 8px; }}
            .news-item h3 {{ margin: 0 0 8px; font-size: 16px; color: #333; }}
            .news-item p {{ margin: 0 0 8px; font-size: 14px; color: #666; }}
            .news-item a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
            .news-item a:hover {{ text-decoration: underline; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            .footer a {{ color: #667eea; text-decoration: none; }}
            .no-news {{ color: #999; font-style: italic; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Crypto Chatbot Newsletter</h1>
                <p>Your Weekly Digest</p>
            </div>
            <div class="content">
                <div class="greeting">
                    Hi {subscriber_name}! 👋
                    <br><br>
                    Here's your weekly roundup of the topics you're following:
                </div>
    """
    
    # Add sections for each topic
    for topic_id in topics:
        topic_name = TOPIC_NAMES.get(topic_id, topic_id)
        news_articles = news_by_topic.get(topic_id, [])
        
        html += f"""
                <div class="topic-section">
                    <div class="topic-title">{topic_name}</div>
        """
        
        # Add price data if available
        price_data = get_price_data_for_topic(topic_id)
        if price_data:
            price_type = price_data.get('type', 'Current Price')
            html += f"""
                    <div class="price-box">
                        <div style="color: #666; font-size: 14px;">{price_type}</div>
                        <div class="price">{price_data['price']}</div>
                        <div style="color: #999; font-size: 12px;">as of {datetime.now().strftime('%B %d, %Y')}</div>
                    </div>
            """
        
        # Add news articles
        if news_articles:
            for article in news_articles:
                title = article.get('title', 'No title')
                url = article.get('url', '#')
                source = article.get('source', {}).get('title', 'Unknown')
                published = article.get('published_at', '')
                
                html += f"""
                    <div class="news-item">
                        <h3>{title}</h3>
                        <p style="color: #999; font-size: 12px;">📰 {source}</p>
                        <a href="{url}" target="_blank">Read more →</a>
                    </div>
                """
        else:
            html += '<p class="no-news">No news articles available for this topic this week.</p>'
        
        html += "</div>"
    
    # Email footer
    html += f"""
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 14px;">
                        💡 Want to explore more? <a href="http://localhost:3000" style="color: #667eea;">Visit Crypto Chatbot</a>
                    </p>
                </div>
            </div>
            <div class="footer">
                <p>You're receiving this because you subscribed to our newsletter.</p>
                <p>Crypto Chatbot &copy; {datetime.now().year} | Powered by AI</p>
                <p><a href="#">Unsubscribe</a> | <a href="#">Manage Preferences</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_newsletters_to_all_subscribers():
    """
    Main function to generate and send newsletters to all subscribers
    This should be run weekly (e.g., via cron job every Monday)
    """
    print("=" * 70)
    print("📧 NEWSLETTER GENERATION STARTED")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Get all unique topics from topic names
    all_topics = list(TOPIC_NAMES.keys())
    
    # Collect news for each topic (do this once for all subscribers)
    print("\n📰 Collecting news for all topics...")
    news_by_topic = {}
    
    for topic_id in all_topics:
        print(f"   • Fetching news for: {TOPIC_NAMES.get(topic_id, topic_id)}")
        news_articles = collect_news_for_topic(topic_id, limit=3)
        news_by_topic[topic_id] = news_articles
        print(f"     ✓ Found {len(news_articles)} articles")
    
    # Get subscribers for all topics
    print("\n👥 Getting subscribers...")
    subscribers = get_subscribers_by_topics(all_topics)
    print(f"   ✓ Found {len(subscribers)} subscribers")
    
    if not subscribers:
        print("\n⚠️  No subscribers found!")
        return
    
    # Send newsletter to each subscriber
    print("\n📨 Sending newsletters...")
    success_count = 0
    error_count = 0
    
    for subscriber in subscribers:
        email = subscriber['email']
        name = subscriber.get('name', 'User')
        topics = subscriber['topics']
        
        print(f"\n   → Sending to: {email}")
        print(f"      Topics: {', '.join([TOPIC_NAMES.get(t, t) for t in topics])}")
        
        # Generate personalized newsletter
        html_content = generate_newsletter_html(name, topics, news_by_topic)
        
        # Generate subject line
        topic_count = len(topics)
        subject = f"Your Weekly Crypto Digest - {topic_count} Topic{'s' if topic_count > 1 else ''} Update"
        
        # Send email via Brevo
        result = send_newsletter(email, subject, html_content, topics)
        
        if result.get('success'):
            print(f"      ✅ Sent successfully!")
            success_count += 1
        else:
            print(f"      ❌ Failed: {result.get('message')}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 NEWSLETTER SENDING COMPLETE")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {error_count}")
    print(f"   📧 Total: {len(subscribers)}")
    print("=" * 70)


def test_newsletter_generation():
    """
    Test function to generate a sample newsletter without sending
    """
    print("🧪 Testing Newsletter Generation")
    print("=" * 70)
    
    # Test with sample data
    test_topics = ['bitcoin', 'ethereum', 'nft-art']
    
    print("\n📰 Collecting news for test topics...")
    news_by_topic = {}
    for topic_id in test_topics:
        print(f"   • {TOPIC_NAMES.get(topic_id, topic_id)}")
        news = collect_news_for_topic(topic_id, limit=3)
        news_by_topic[topic_id] = news
        print(f"     ✓ Found {len(news)} articles")
    
    print("\n📧 Generating newsletter HTML...")
    html_content = generate_newsletter_html("Test User", test_topics, news_by_topic)
    
    # Save to file for preview
    output_file = "newsletter_preview.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Newsletter generated successfully!")
    print(f"📁 Preview saved to: {output_file}")
    print(f"📊 Newsletter includes {len(test_topics)} topics")
    
    return html_content


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode - generate preview without sending
        test_newsletter_generation()
    elif len(sys.argv) > 1 and sys.argv[1] == '--send':
        # Send newsletters to all subscribers
        send_newsletters_to_all_subscribers()
    else:
        print("Usage:")
        print("  python newsletter_generator.py --test   (Generate preview)")
        print("  python newsletter_generator.py --send   (Send to all subscribers)")
