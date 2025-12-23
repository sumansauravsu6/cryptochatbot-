"""
Newsletter subscription API using Brevo (formerly Sendinblue)
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
BREVO_API_URL = "https://api.brevo.com/v3"


def subscribe_to_newsletter(email, topics, user_name="User"):
    """
    Subscribe a user to the newsletter with selected topics
    
    Args:
        email: User's email address
        topics: List of topic IDs user is interested in
        user_name: User's name
    
    Returns:
        dict: Response with success status
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY
    }
    
    # Prepare contact attributes with topics
    attributes = {
        "FIRSTNAME": user_name.split()[0] if user_name else "User",
        "TOPICS": ",".join(topics),
        "SUBSCRIBED_DATE": datetime.now().strftime("%Y-%m-%d"),
        "SOURCE": "Crypto Chatbot"
    }
    
    print(f"DEBUG - Subscribing with attributes: {attributes}")
    
    # Create or update contact in Brevo
    # Note: Using SMS field as workaround for topics since custom attributes need to be created in Brevo dashboard
    contact_data = {
        "email": email,
        "attributes": {
            "FIRSTNAME": user_name.split()[0] if user_name else "User",
            "LASTNAME": ",".join(topics)  # Store topics in LASTNAME as workaround
        },
        "updateEnabled": True
    }
    
    try:
        # Add contact to Brevo
        response = requests.post(
            f"{BREVO_API_URL}/contacts",
            json=contact_data,
            headers=headers
        )
        
        print(f"DEBUG - Brevo response status: {response.status_code}")
        print(f"DEBUG - Brevo response: {response.text}")
        
        if response.status_code in [201, 204]:
            return {
                "success": True,
                "message": "Successfully subscribed to newsletter",
                "email": email
            }
        elif response.status_code == 400:
            # Contact might already exist, try to update
            response = requests.put(
                f"{BREVO_API_URL}/contacts/{email}",
                json={"attributes": {"FIRSTNAME": user_name.split()[0] if user_name else "User", "LASTNAME": ",".join(topics)}},
                headers=headers
            )
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": "Newsletter subscription updated",
                    "email": email
                }
        
        return {
            "success": False,
            "message": f"Failed to subscribe: {response.text}",
            "status_code": response.status_code
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error subscribing to newsletter: {str(e)}"
        }


def send_newsletter(recipient_email, subject, html_content, topics):
    """
    Send a newsletter email to a subscriber
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject
        html_content: HTML content of the email
        topics: Topics the user is subscribed to
    
    Returns:
        dict: Response with success status
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY
    }
    
    email_data = {
        "sender": {
            "name": "Crypto Chatbot Newsletter",
            "email": "newsletter@cryptochatbot.com"  # Replace with your verified sender
        },
        "to": [
            {
                "email": recipient_email
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
        "tags": ["newsletter", "weekly-digest"]
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


def get_subscribers_by_topics(topics):
    """
    Get all subscribers interested in specific topics
    
    Args:
        topics: List of topic IDs
    
    Returns:
        list: List of subscriber email addresses
    """
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY
    }
    
    try:
        # Get all contacts from list
        response = requests.get(
            f"{BREVO_API_URL}/contacts/lists/2/contacts",  # List ID 2
            headers=headers,
            params={"limit": 500}
        )
        
        if response.status_code == 200:
            contacts = response.json().get("contacts", [])
            
            # Filter contacts by topics
            matching_subscribers = []
            for contact in contacts:
                subscriber_topics = contact.get("attributes", {}).get("TOPICS", "").split(",")
                if any(topic in subscriber_topics for topic in topics):
                    matching_subscribers.append({
                        "email": contact["email"],
                        "name": contact.get("attributes", {}).get("FIRSTNAME", "User"),
                        "topics": subscriber_topics
                    })
            
            return matching_subscribers
        else:
            return []
            
    except Exception as e:
        print(f"Error getting subscribers: {e}")
        return []


def unsubscribe_from_newsletter(email):
    """
    Unsubscribe a user from the newsletter
    
    Args:
        email: User's email address
    
    Returns:
        dict: Response with success status
    """
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY
    }
    
    try:
        # Remove from list or delete contact
        response = requests.delete(
            f"{BREVO_API_URL}/contacts/{email}",
            headers=headers
        )
        
        if response.status_code == 204:
            return {
                "success": True,
                "message": "Successfully unsubscribed from newsletter"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to unsubscribe: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error unsubscribing: {str(e)}"
        }

def get_subscriber_info(email):
    """
    Get subscriber information including their topics
    
    Args:
        email: User's email address
    
    Returns:
        dict: Subscriber information with topics
    """
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY
    }
    
    try:
        response = requests.get(
            f"{BREVO_API_URL}/contacts/{email}",
            headers=headers
        )
        
        if response.status_code == 200:
            contact = response.json()
            # Topics are stored in LASTNAME field as workaround
            topics_str = contact.get("attributes", {}).get("LASTNAME", "")
            topics = [t.strip() for t in topics_str.split(",") if t.strip()]
            
            return {
                "success": True,
                "email": email,
                "name": contact.get("attributes", {}).get("FIRSTNAME", "User"),
                "topics": topics,
                "subscribed_date": contact.get("createdAt", "")
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "message": "Subscriber not found",
                "topics": []
            }
        else:
            return {
                "success": False,
                "message": f"Failed to get subscriber info: {response.text}",
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
    Update subscriber's topics
    
    Args:
        email: User's email address
        topics: List of topic IDs to subscribe to
        user_name: User's name
        mode: 'merge' to add new topics, 'replace' to replace all topics (default)
    
    Returns:
        dict: Response with success status
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY
    }
    
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
        # Replace all topics with the new list
        final_topics = topics
    
    # Validate that we have at least one topic
    if not final_topics:
        return {
            "success": False,
            "message": "At least one topic is required"
        }
    
    # Update contact attributes (using LASTNAME to store topics)
    attributes = {
        "FIRSTNAME": user_name.split()[0] if user_name else "User",
        "LASTNAME": ",".join(final_topics)
    }
    
    try:
        response = requests.put(
            f"{BREVO_API_URL}/contacts/{email}",
            json={"attributes": attributes},
            headers=headers
        )
        
        if response.status_code == 204:
            return {
                "success": True,
                "message": "Topics updated successfully",
                "email": email,
                "topics": final_topics
            }
        else:
            return {
                "success": False,
                "message": f"Failed to update topics: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating topics: {str(e)}"
        }