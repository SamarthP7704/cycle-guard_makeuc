"""
Simple test client for CycleGuard AI API
"""
import requests
import os
import sys


API_BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_dropoff(image_path: str):
    """Test dropoff endpoint"""
    print(f"Testing dropoff with image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return None
    
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        response = requests.post(f"{API_BASE_URL}/api/dropoff", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}\n")
    return result.get('event_id')


def test_pickup(image_path: str):
    """Test pickup endpoint"""
    print(f"Testing pickup with image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return None
    
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        response = requests.post(f"{API_BASE_URL}/api/pickup", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}\n")
    return result.get('event_id')


def test_get_events():
    """Test get events endpoint"""
    print("Testing get events endpoint...")
    response = requests.get(f"{API_BASE_URL}/api/events?limit=10")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Events count: {result.get('count', 0)}\n")
    return result.get('events', [])


def test_get_event(event_id: str):
    """Test get specific event endpoint"""
    print(f"Testing get event endpoint for: {event_id}")
    response = requests.get(f"{API_BASE_URL}/api/events/{event_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Event: {result}\n")
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("CycleGuard AI Test Client")
    print("=" * 50)
    print()
    
    # Test health
    test_health()
    
    # Test dropoff (if image provided)
    if len(sys.argv) > 1:
        dropoff_image = sys.argv[1]
        event_id = test_dropoff(dropoff_image)
        
        # Test pickup (if second image provided)
        if len(sys.argv) > 2:
            pickup_image = sys.argv[2]
            test_pickup(pickup_image)
        
        # Test get events
        events = test_get_events()
        
        # Test get specific event
        if event_id:
            test_get_event(event_id)
    else:
        print("Usage: python test_client.py <dropoff_image_path> [pickup_image_path]")
        print("Example: python test_client.py person1.jpg person2.jpg")

