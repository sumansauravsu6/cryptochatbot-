"""
Test newsletter subscription API
"""
import requests
import json

BASE_URL = "http://localhost:5000/api/newsletter"

# Test 1: Subscribe to newsletter
print("=" * 60)
print("Test 1: Subscribe to Newsletter")
print("=" * 60)

subscribe_data = {
    "email": "test@example.com",
    "topics": ["bitcoin", "ethereum", "nft-art"],
    "userName": "Test User"
}

try:
    response = requests.post(
        f"{BASE_URL}/subscribe",
        json=subscribe_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Subscription successful!")
    else:
        print("❌ Subscription failed")
        
except requests.exceptions.ConnectionError:
    print("❌ Error: Could not connect to Flask server")
    print("Make sure Flask is running: python flask_server.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test 2: Try to subscribe with missing topics")
print("=" * 60)

invalid_data = {
    "email": "test2@example.com",
    "topics": []
}

try:
    response = requests.post(
        f"{BASE_URL}/subscribe",
        json=invalid_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 400:
        print("✅ Validation working correctly!")
    else:
        print("⚠️  Expected 400 error")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Newsletter API Test Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Check Brevo dashboard for new contact")
print("2. Verify topics are saved correctly")
print("3. Test from React UI")
