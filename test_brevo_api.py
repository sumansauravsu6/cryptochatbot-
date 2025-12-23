"""
Test script to verify Brevo API is working correctly
"""
import os
from dotenv import load_dotenv
from newsletter_api import subscribe_to_newsletter, get_subscriber_info

load_dotenv()

def test_brevo_api():
    """Test Brevo API subscription and retrieval"""
    
    test_email = "test@example.com"
    test_topics = ["bitcoin", "ethereum"]
    test_name = "Test User"
    
    print("=" * 70)
    print("TESTING BREVO API")
    print("=" * 70)
    
    # Test 1: Subscribe
    print("\n1. Testing subscription...")
    result = subscribe_to_newsletter(test_email, test_topics, test_name)
    print(f"   Result: {result}")
    
    if result.get('success'):
        print("   ✅ Subscription successful!")
    else:
        print("   ❌ Subscription failed!")
        print(f"   Error: {result.get('message')}")
        return
    
    # Test 2: Retrieve subscription
    print("\n2. Testing subscription retrieval...")
    result = get_subscriber_info(test_email)
    print(f"   Result: {result}")
    
    if result.get('success'):
        print("   ✅ Retrieval successful!")
        print(f"   Email: {result.get('email')}")
        print(f"   Name: {result.get('name')}")
        print(f"   Topics: {result.get('topics')}")
    else:
        print("   ❌ Retrieval failed!")
        print(f"   Error: {result.get('message')}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    test_brevo_api()
