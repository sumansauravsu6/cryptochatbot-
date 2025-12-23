"""
Cron Job Script for Sending Newsletters
This script is designed to be run by a scheduler (cron, Render Cron, etc.)

Usage:
  python cron_newsletter.py          # Send newsletters
  python cron_newsletter.py --test   # Test without sending
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import newsletter functions
from newsletter_generator import send_newsletters_to_all_subscribers, test_newsletter_generation


def log_message(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_newsletter_job():
    """
    Main function to run the newsletter job
    Called by cron scheduler
    """
    log_message("🚀 Starting Newsletter Cron Job")
    log_message("=" * 50)
    
    # Check if required environment variables are set
    required_vars = ['BREVO_API_KEY', 'CRYPTOPANIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        log_message(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:
        # Send newsletters to all subscribers
        log_message("📧 Sending newsletters to subscribers...")
        send_newsletters_to_all_subscribers()
        log_message("✅ Newsletter job completed successfully")
        
    except Exception as e:
        log_message(f"❌ Newsletter job failed: {str(e)}")
        sys.exit(1)


def run_test_job():
    """
    Test the newsletter generation without sending
    """
    log_message("🧪 Running Newsletter Test Job")
    log_message("=" * 50)
    
    try:
        test_newsletter_generation()
        log_message("✅ Test completed successfully")
        
    except Exception as e:
        log_message(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_test_job()
    else:
        run_newsletter_job()
