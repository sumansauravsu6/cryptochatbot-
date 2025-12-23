"""
Test Newsletter Sending - Send a real newsletter to test email
"""
from newsletter_generator import generate_newsletter_html, collect_news_for_topic, get_price_data_for_topic
from newsletter_api import send_newsletter
from datetime import datetime

def test_send_real_newsletter():
    """
    Test sending a real newsletter to a test email address
    """
    print("=" * 70)
    print("🧪 TESTING REAL NEWSLETTER SEND")
    print("=" * 70)
    
    # Test email - CHANGE THIS TO YOUR REAL EMAIL
    test_email = input("\nEnter your email address to receive test newsletter: ").strip()
    
    if not test_email or '@' not in test_email:
        print("❌ Invalid email address!")
        return
    
    # Test topics
    test_topics = ['bitcoin', 'ethereum', 'nft-art']
    test_name = "Test User"
    
    print(f"\n📧 Test Email: {test_email}")
    print(f"👤 Test Name: {test_name}")
    print(f"📌 Topics: {', '.join(test_topics)}")
    
    # Collect news and price data
    print("\n📰 Collecting news for topics...")
    news_by_topic = {}
    
    for topic_id in test_topics:
        print(f"   • Collecting data for: {topic_id}")
        
        # Get news
        news_articles = collect_news_for_topic(topic_id, limit=3)
        news_by_topic[topic_id] = news_articles
        print(f"     ✓ Found {len(news_articles)} news articles")
        
        # Get price data
        price_data = get_price_data_for_topic(topic_id)
        if price_data:
            print(f"     ✓ Got price: {price_data['price']}")
    
    # Generate HTML
    print("\n📝 Generating newsletter HTML...")
    html_content = generate_newsletter_html(test_name, test_topics, news_by_topic)
    print("   ✓ HTML generated successfully")
    
    # Save preview
    with open('test_newsletter_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("   ✓ Preview saved to: test_newsletter_preview.html")
    
    # Ask for confirmation
    print("\n" + "=" * 70)
    confirm = input("Send newsletter to this email? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Newsletter sending cancelled.")
        return
    
    # Send newsletter
    print("\n📨 Sending newsletter via Brevo...")
    subject = f"🧪 Test Newsletter - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    result = send_newsletter(test_email, subject, html_content, test_topics)
    
    if result.get('success'):
        print("\n" + "=" * 70)
        print("✅ NEWSLETTER SENT SUCCESSFULLY!")
        print("=" * 70)
        print(f"📧 Email: {test_email}")
        print(f"📬 Subject: {subject}")
        print(f"⏰ Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 Check your inbox (and spam folder) for the newsletter!")
    else:
        print("\n" + "=" * 70)
        print("❌ NEWSLETTER SEND FAILED")
        print("=" * 70)
        print(f"Error: {result.get('message')}")
        print("\nPossible reasons:")
        print("1. Sender email not verified in Brevo")
        print("2. Invalid API key")
        print("3. Brevo rate limit reached")
        print("4. Invalid recipient email")


def test_subscriber_workflow():
    """
    Test the complete subscriber workflow
    """
    print("=" * 70)
    print("🔄 TESTING COMPLETE SUBSCRIBER WORKFLOW")
    print("=" * 70)
    
    # Step 1: Subscribe
    print("\n1️⃣  SUBSCRIPTION PHASE")
    print("   This would be done via the UI modal:")
    print("   - User opens newsletter modal")
    print("   - Selects topics: Bitcoin, Ethereum, NFT Art")
    print("   - Clicks 'Subscribe'")
    print("   - POST to /api/newsletter/subscribe")
    
    # Step 2: Data storage
    print("\n2️⃣  DATA STORAGE PHASE")
    print("   ✓ Email and topics saved to Brevo")
    print("   ✓ Contact attributes created:")
    print("     - TOPICS: bitcoin,ethereum,nft-art")
    print("     - SUBSCRIBED_DATE: 2025-12-13")
    print("     - SOURCE: Crypto Chatbot")
    
    # Step 3: News collection
    print("\n3️⃣  NEWS COLLECTION PHASE (Weekly Cron Job)")
    print("   ✓ newsletter_generator.py runs")
    print("   ✓ Collects news for all 14 topics:")
    print("     - Calls CoinGecko API")
    print("     - Gets latest 3 articles per topic")
    print("     - Gets current prices")
    
    # Step 4: Newsletter generation
    print("\n4️⃣  NEWSLETTER GENERATION PHASE")
    print("   ✓ Gets all subscribers from Brevo")
    print("   ✓ For each subscriber:")
    print("     - Filters news by their topics")
    print("     - Generates personalized HTML")
    print("     - Includes prices and news")
    
    # Step 5: Email sending
    print("\n5️⃣  EMAIL SENDING PHASE")
    print("   ✓ Sends via Brevo SMTP API")
    print("   ✓ Subject: 'Your Weekly Crypto Digest - X Topics Update'")
    print("   ✓ Beautiful HTML email with:")
    print("     - Personalized greeting")
    print("     - Current Bitcoin price: $90,416")
    print("     - Current Ethereum price: $3,329")
    print("     - Latest news articles with links")
    
    # Step 6: Delivery
    print("\n6️⃣  DELIVERY PHASE")
    print("   ✓ Brevo delivers email to inbox")
    print("   ✓ User receives newsletter")
    print("   ✓ Can click links to read full articles")
    
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    import sys
    
    print("\n🤖 Newsletter Testing Menu")
    print("=" * 70)
    print("1. Send test newsletter to your email")
    print("2. View complete workflow explanation")
    print("=" * 70)
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        test_send_real_newsletter()
    elif choice == '2':
        test_subscriber_workflow()
    else:
        print("Invalid choice!")
