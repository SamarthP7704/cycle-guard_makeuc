"""
Example usage of CycleGuard AI API
"""
import requests
import time
from pathlib import Path


API_BASE_URL = "http://localhost:8000"


def example_dropoff_pickup_flow():
    """Example: Complete flow from dropoff to pickup"""
    
    print("=" * 60)
    print("CycleGuard AI - Example Usage")
    print("=" * 60)
    print()
    
    # Step 1: Register a dropoff event
    print("Step 1: Registering dropoff event...")
    print("(Note: Replace with actual image paths)")
    
    dropoff_image = "example_dropoff.jpg"  # Replace with your image path
    if not Path(dropoff_image).exists():
        print(f"⚠️  Image not found: {dropoff_image}")
        print("   Please provide a valid image path for dropoff")
        return
    
    try:
        with open(dropoff_image, 'rb') as f:
            files = {'file': (Path(dropoff_image).name, f, 'image/jpeg')}
            response = requests.post(f"{API_BASE_URL}/api/dropoff", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            dropoff_event_id = result['event_id']
            print(f"✅ Dropoff event registered: {dropoff_event_id}")
            print(f"   Person detected: {result['detections']['person_detected']}")
            print(f"   Cycle detected: {result['detections']['cycle_detected']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.json()}")
            return
    except Exception as e:
        print(f"❌ Error registering dropoff: {e}")
        return
    
    print()
    time.sleep(2)  # Simulate time passing
    
    # Step 2: Register a pickup event (same person)
    print("Step 2: Registering pickup event (same person)...")
    pickup_image_same = "example_pickup_same.jpg"  # Replace with your image path
    
    if Path(pickup_image_same).exists():
        try:
            with open(pickup_image_same, 'rb') as f:
                files = {'file': (Path(pickup_image_same).name, f, 'image/jpeg')}
                response = requests.post(f"{API_BASE_URL}/api/pickup", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                match_result = result['match_result']
                print(f"✅ Pickup event processed: {result['event_id']}")
                print(f"   Same person: {match_result['is_same_person']}")
                print(f"   Similarity score: {match_result['similarity_score']:.2f}")
                print(f"   Confidence: {match_result['confidence']}")
                print(f"   Alert sent: {result['alert_sent']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.json()}")
        except Exception as e:
            print(f"❌ Error registering pickup: {e}")
    else:
        print(f"⚠️  Image not found: {pickup_image_same}")
    
    print()
    time.sleep(2)
    
    # Step 3: Register a pickup event (different person)
    print("Step 3: Registering pickup event (different person)...")
    pickup_image_different = "example_pickup_different.jpg"  # Replace with your image path
    
    if Path(pickup_image_different).exists():
        try:
            with open(pickup_image_different, 'rb') as f:
                files = {'file': (Path(pickup_image_different).name, f, 'image/jpeg')}
                response = requests.post(f"{API_BASE_URL}/api/pickup", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                match_result = result['match_result']
                print(f"✅ Pickup event processed: {result['event_id']}")
                print(f"   Same person: {match_result['is_same_person']}")
                print(f"   Similarity score: {match_result['similarity_score']:.2f}")
                print(f"   Confidence: {match_result['confidence']}")
                print(f"   Alert sent: {result['alert_sent']}")
                
                if result['alert_sent']:
                    print("   🚨 SECURITY ALERT TRIGGERED!")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.json()}")
        except Exception as e:
            print(f"❌ Error registering pickup: {e}")
    else:
        print(f"⚠️  Image not found: {pickup_image_different}")
    
    print()
    
    # Step 4: Get all events
    print("Step 4: Retrieving all events...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/events?limit=10")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {result['count']} events")
            for event in result['events']:
                print(f"   - {event['event_type']}: {event['event_id']} at {event['timestamp']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error retrieving events: {e}")
    
    print()
    print("=" * 60)
    print("Example completed!")
    print("=" * 60)


def example_simple_api_call():
    """Simple example of API usage"""
    print("\nSimple API Usage Example:")
    print("-" * 40)
    
    # Health check
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            print(f"   Status: {response.json()['status']}")
        else:
            print("❌ API health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the server is running: uvicorn main:app --reload")


if __name__ == "__main__":
    # First, check if API is running
    example_simple_api_call()
    
    # Then run the full example
    print("\n")
    example_dropoff_pickup_flow()

