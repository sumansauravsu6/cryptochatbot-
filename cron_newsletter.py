"""
Cron Job Script for Sending Newsletters (Standalone version)
Uses direct REST API calls - no supabase library dependency

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


# ==============================================
# DIRECT SUPABASE REST API FUNCTIONS
# ==============================================

def get_supabase_headers():
    """Get headers for Supabase REST API"""
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    return {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }


def get_all_active_subscribers_rest():
    """Get all active subscribers using direct REST API"""
    supabase_url = os.getenv('SUPABASE_URL')
    
    if not supabase_url:
        print("⚠️ SUPABASE_URL not configured")
        return []
    
    url = f"{supabase_url}/rest/v1/newsletter_subscriptions"
    params = {
        'select': '*',
        'is_active': 'eq.true'
    }
    
    try:
        response = requests.get(url, headers=get_supabase_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching subscribers: {e}")
        return []


# ==============================================
# LOGGING
# ==============================================

def log_message(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


# ==============================================
# MAIN JOB
# ==============================================

def run_newsletter_job():
    """Main function to run the newsletter job"""
    log_message("🚀 Starting Newsletter Cron Job")
    log_message("=" * 50)
    
    # Check environment variables
    required_vars = ['BREVO_API_KEY', 'CRYPTOPANIC_API_KEY', 'SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        log_message(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    log_message("✅ All environment variables configured")
    
    try:
        # Get subscribers directly via REST API first to test connection
        log_message("📧 Testing Supabase connection...")
        subscribers = get_all_active_subscribers_rest()
        log_message(f"   Found {len(subscribers)} active subscribers")
        
        if not subscribers:
            log_message("⚠️ No active subscribers found. Exiting.")
            return
        
        # Now import and run the full newsletter generator
        # This uses the newsletter_api module which has the supabase client
        log_message("📧 Generating and sending newsletters...")
        
        # Import here to avoid supabase import issues at module level
        from newsletter_generator import (
            TOPIC_NAMES, collect_news_for_topic, 
            generate_newsletter_html, send_newsletter
        )
        
        # Collect unique topics
        all_subscriber_topics = set()
        for subscriber in subscribers:
            all_subscriber_topics.update(subscriber.get('topics', []))
        
        log_message(f"📋 Topics to fetch: {len(all_subscriber_topics)}")
        
        # Collect top 3 news for each topic
        log_message("📰 Collecting TOP 3 news for each topic...")
        news_by_topic = {}
        for topic_id in all_subscriber_topics:
            topic_name = TOPIC_NAMES.get(topic_id, topic_id)
            log_message(f"   • Fetching: {topic_name}")
            news_articles = collect_news_for_topic(topic_id, limit=3)
            news_by_topic[topic_id] = news_articles
            log_message(f"     ✓ Found {len(news_articles)} articles")
        
        # Send to each subscriber
        log_message("📨 Sending personalized newsletters...")
        success_count = 0
        error_count = 0
        
        for subscriber in subscribers:
            email = subscriber.get('user_email')
            name = subscriber.get('user_name', 'User')
            topics = subscriber.get('topics', [])
            
            if not email or not topics:
                continue
            
            log_message(f"   → Sending to: {email}")
            
            html_content = generate_newsletter_html(name, topics, news_by_topic)
            subject = f"Your Weekly Crypto Digest - {len(topics)} Topic{'s' if len(topics) > 1 else ''} Update"
            
            result = send_newsletter(email, subject, html_content, topics)
            
            if result.get('success'):
                log_message(f"      ✅ Sent!")
                success_count += 1
            else:
                log_message(f"      ❌ Failed: {result.get('message')}")
                error_count += 1
        
        log_message("=" * 50)
        log_message(f"📊 Results: {success_count} sent, {error_count} failed")
        log_message("✅ Newsletter job completed")
        
    except Exception as e:
        log_message(f"❌ Newsletter job failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_test_job():
    """Test the newsletter generation without sending"""
    log_message("🧪 Running Newsletter Test Job")
    log_message("=" * 50)
    
    try:
        # Test Supabase connection using REST API
        log_message("Testing Supabase connection...")
        subscribers = get_all_active_subscribers_rest()
        log_message(f"✅ Found {len(subscribers)} subscribers")
        
        for sub in subscribers[:3]:  # Show first 3
            log_message(f"   - {sub.get('user_email')}: {sub.get('topics')}")
        
        log_message("✅ Test completed successfully")
        
    except Exception as e:
        log_message(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_test_job()
    else:
        run_newsletter_job()
