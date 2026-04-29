import requests

# Test similarity-check endpoint
url = "http://localhost:5000/api/similarity-check"
data = {"query": "test query"}

print("Testing similarity-check endpoint...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Endpoint is working!")
except Exception as e:
    print(f"❌ Error: {e}")
