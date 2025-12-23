"""
Newsletter subscription API using Supabase for storage and Brevo for sending emails
- User preferences stored in Supabase
- Users can edit their topic choices
- Newsletter sending fetches preferences from Supabase
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for backend

# Brevo Configuration (for sending emails only)
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
BREVO_API_URL = "https://api.brevo.com/v3"

# Initialize Supabase client
supabase: Client = None

def get_supabase_client():
    """Get or create Supabase client"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            print("⚠️ Supabase credentials not configured")
            return None
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return supabase


# ============================================
# SUPABASE SUBSCRIPTION FUNCTIONS
# ============================================

def subscribe_to_newsletter(email, topics, user_name="User"):
    """
    Subscribe a user to the newsletter - stores preferences in Supabase
    
    Args:
        email: User's email address
        topics: List of topic IDs user is interested in
        user_name: User's name
    
    Returns:
        dict: Response with success status
    """
    client = get_supabase_client()
    if not client:
        return {"success": False, "message": "Supabase not configured"}
    
    try:
        # Check if user already exists
        existing = client.table('newsletter_subscriptions').select('*').eq('user_email', email).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing subscription
            result = client.table('newsletter_subscriptions').update({
                'topics': topics,
                'user_name': user_name,
                'is_active': True,
                'updated_at': datetime.now().isoformat()
            }).eq('user_email', email).execute()
            
            return {
                "success": True,
                "message": "Newsletter subscription updated",
                "email": email,
                "topics": topics
            }
        else:
            # Create new subscription
            result = client.table('newsletter_subscriptions').insert({
                'user_email': email,
                'user_name': user_name,
                'topics': topics,
                'is_active': True
            }).execute()
            
            return {
                "success": True,
                "message": "Successfully subscribed to newsletter",
                "email": email,
                "topics": topics
            }
            
    except Exception as e:
        print(f"Error subscribing to newsletter: {e}")
        return {
            "success": False,
            "message": f"Error subscribing to newsletter: {str(e)}"
        }


def unsubscribe_from_newsletter(email):
    """
    Unsubscribe a user from the newsletter (soft delete - sets is_active to False)
    
    Args:
        email: User's email address
    
    Returns:
        dict: Response with success status
    """
    client = get_supabase_client()
    if not client:
        return {"success": False, "message": "Supabase not configured"}
    
    try:
        result = client.table('newsletter_subscriptions').update({
            'is_active': False,
            'updated_at': datetime.now().isoformat()
        }).eq('user_email', email).execute()
        
        return {
            "success": True,
            "message": "Successfully unsubscribed from newsletter"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error unsubscribing: {str(e)}"
        }


def get_subscriber_info(email):
    """
    Get subscriber information including their topics from Supabase
    
    Args:
        email: User's email address
    
    Returns:
        dict: Subscriber information with topics
    """
    client = get_supabase_client()
    if not client:
        return {"success": False, "message": "Supabase not configured", "topics": []}
    
    try:
        result = client.table('newsletter_subscriptions').select('*').eq('user_email', email).execute()
        
        if result.data and len(result.data) > 0:
            subscriber = result.data[0]
            return {
                "success": True,
                "email": email,
                "name": subscriber.get('user_name', 'User'),
                "topics": subscriber.get('topics', []),
                "is_active": subscriber.get('is_active', False),
                "subscribed_date": subscriber.get('created_at', '')
            }
        else:
            return {
                "success": False,
                "message": "Subscriber not found",
                "topics": []
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting subscriber info: {str(e)}",
            "topics": []
        }


def update_subscriber_topics(email, topics, user_name="User", mode="replace"):
    """
    Update subscriber's topics in Supabase
    
    Args:
        email: User's email address
        topics: List of topic IDs to subscribe to
        user_name: User's name
        mode: 'merge' to add new topics, 'replace' to replace all topics (default)
    
    Returns:
        dict: Response with success status
    """
    client = get_supabase_client()
    if not client:
        return {"success": False, "message": "Supabase not configured"}
    
    if mode == "merge":
        # Get existing subscriber info
        existing = get_subscriber_info(email)
        
        if existing.get('success'):
            # Merge existing topics with new topics (avoid duplicates)
            existing_topics = existing.get('topics', [])
            final_topics = list(set(existing_topics + topics))
        else:
            final_topics = topics
    else:  # mode == "replace"
        final_topics = topics
    
    # Validate that we have at least one topic
    if not final_topics:
        return {
            "success": False,
            "message": "At least one topic is required"
        }
    
    try:
        # Check if user exists
        existing = client.table('newsletter_subscriptions').select('*').eq('user_email', email).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing
            result = client.table('newsletter_subscriptions').update({
                'topics': final_topics,
                'user_name': user_name,
                'is_active': True,
                'updated_at': datetime.now().isoformat()
            }).eq('user_email', email).execute()
        else:
            # Create new
            result = client.table('newsletter_subscriptions').insert({
                'user_email': email,
                'user_name': user_name,
                'topics': final_topics,
                'is_active': True
            }).execute()
        
        return {
            "success": True,
            "message": "Topics updated successfully",
            "email": email,
            "topics": final_topics
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating topics: {str(e)}"
        }


def get_all_active_subscribers():
    """
    Get all active newsletter subscribers from Supabase
    
    Returns:
        list: List of active subscribers with their topics
    """
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        result = client.table('newsletter_subscriptions').select('*').eq('is_active', True).execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"Error getting subscribers: {e}")
        return []


def get_subscribers_by_topics(topics):
    """
    Get all active subscribers interested in specific topics
    
    Args:
        topics: List of topic IDs
    
    Returns:
        list: List of subscriber dictionaries
    """
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        # Get all active subscribers
        result = client.table('newsletter_subscriptions').select('*').eq('is_active', True).execute()
        
        if not result.data:
            return []
        
        # Filter subscribers who have at least one matching topic
        matching_subscribers = []
        for subscriber in result.data:
            subscriber_topics = subscriber.get('topics', [])
            if any(topic in subscriber_topics for topic in topics):
                matching_subscribers.append({
                    "email": subscriber['user_email'],
                    "name": subscriber.get('user_name', 'User'),
                    "topics": subscriber_topics
                })
        
        return matching_subscribers
        
    except Exception as e:
        print(f"Error getting subscribers by topics: {e}")
        return []


# ============================================
# BREVO EMAIL SENDING FUNCTIONS
# ============================================

def send_newsletter(recipient_email, subject, html_content, topics):
    """
    Send a newsletter email to a subscriber using Brevo
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject
        html_content: HTML content of the email
        topics: Topics the user is subscribed to
    
    Returns:
        dict: Response with success status
    """
    if not BREVO_API_KEY:
        return {"success": False, "message": "Brevo API key not configured"}
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY
    }
    
    # Get sender email from env or use default
    sender_email = os.getenv('NEWSLETTER_SENDER_EMAIL', 'newsletter@example.com')
    sender_name = os.getenv('NEWSLETTER_SENDER_NAME', 'Crypto Chatbot Newsletter')
    
    email_data = {
        "sender": {
            "name": sender_name,
            "email": sender_email
        },
        "to": [
            {
                "email": recipient_email
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
        "tags": ["newsletter", "crypto", "weekly-digest"]
    }
    
    try:
        response = requests.post(
            f"{BREVO_API_URL}/smtp/email",
            json=email_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "message": "Newsletter sent successfully",
                "messageId": response.json().get("messageId")
            }
        else:
            return {
                "success": False,
                "message": f"Failed to send newsletter: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending newsletter: {str(e)}"
        }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def delete_subscriber(email):
    """
    Permanently delete a subscriber from Supabase (hard delete)
    
    Args:
        email: User's email address
    
    Returns:
        dict: Response with success status
    """
    client = get_supabase_client()
    if not client:
        return {"success": False, "message": "Supabase not configured"}
    
    try:
        result = client.table('newsletter_subscriptions').delete().eq('user_email', email).execute()
        
        return {
            "success": True,
            "message": "Subscriber deleted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting subscriber: {str(e)}"
        }


def get_subscription_stats():
    """
    Get newsletter subscription statistics
    
    Returns:
        dict: Stats including total, active, and topic counts
    """
    client = get_supabase_client()
    if not client:
        return {"success": False, "message": "Supabase not configured"}
    
    try:
        # Get all subscriptions
        all_subs = client.table('newsletter_subscriptions').select('*').execute()
        active_subs = client.table('newsletter_subscriptions').select('*').eq('is_active', True).execute()
        
        # Count topics
        topic_counts = {}
        for sub in (active_subs.data or []):
            for topic in sub.get('topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            "success": True,
            "total_subscribers": len(all_subs.data) if all_subs.data else 0,
            "active_subscribers": len(active_subs.data) if active_subs.data else 0,
            "topic_counts": topic_counts
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting stats: {str(e)}"
        }


# ============================================
# TEST FUNCTION
# ============================================

if __name__ == '__main__':
    print("🧪 Testing Newsletter API with Supabase")
    print("=" * 50)
    
    # Test connection
    client = get_supabase_client()
    if client:
        print("✅ Supabase connected")
    else:
        print("❌ Supabase not configured")
        exit(1)
    
    # Test subscribe
    test_email = "test@example.com"
    result = subscribe_to_newsletter(test_email, ["bitcoin", "ethereum"], "Test User")
    print(f"Subscribe: {result}")
    
    # Test get info
    result = get_subscriber_info(test_email)
    print(f"Get Info: {result}")
    
    # Test update topics
    result = update_subscriber_topics(test_email, ["bitcoin", "defi", "nft-art"], "Test User")
    print(f"Update Topics: {result}")
    
    # Test get all active
    result = get_all_active_subscribers()
    print(f"Active Subscribers: {len(result)}")
    
    # Test stats
    result = get_subscription_stats()
    print(f"Stats: {result}")
    
    print("\n✅ All tests completed!")
