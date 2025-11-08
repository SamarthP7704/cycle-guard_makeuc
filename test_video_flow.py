"""
Test script for CycleGuard AI using video files
Tests the complete flow: dropoff -> pickup (same person) -> pickup (different person)
"""
import requests
import os
import time
from pathlib import Path


API_BASE_URL = "http://localhost:8000"
TEST_VIDEOS_DIR = "test_videos"

# Video file names (update these to match your video files)
DROPOFF_VIDEO = "drop-off.mp4"
PICKUP_SAME_VIDEO = "pickup.mp4"
PICKUP_DIFFERENT_VIDEO = "steal.mp4"

# Alternative extensions to try
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".MP4", ".MOV", ".AVI"]


def find_video_file(base_name: str) -> str:
    """Find video file with any supported extension"""
    for ext in VIDEO_EXTENSIONS:
        video_path = os.path.join(TEST_VIDEOS_DIR, base_name.replace(".mp4", ext))
        if os.path.exists(video_path):
            return video_path
    return None


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Start the server with: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error checking API health: {e}")
        return False


def upload_video(endpoint: str, video_path: str, event_type: str) -> dict:
    """Upload video to API endpoint"""
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return None
    
    print(f"\n📹 Uploading {event_type} video: {os.path.basename(video_path)}")
    print(f"   File size: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")
    
    try:
        # Determine content type based on extension
        ext = Path(video_path).suffix.lower()
        content_type_map = {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska'
        }
        content_type = content_type_map.get(ext, 'video/mp4')
        
        with open(video_path, 'rb') as f:
            files = {'file': (os.path.basename(video_path), f, content_type)}
            print("   ⏳ Processing... (this may take a moment)")
            response = requests.post(
                f"{API_BASE_URL}{endpoint}",
                files=files,
                timeout=60  # Longer timeout for video processing
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success!")
            return result
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detail: {error_detail.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out. Video processing may be taking too long.")
        return None
    except Exception as e:
        print(f"   ❌ Error uploading video: {e}")
        return None


def test_dropoff():
    """Test dropoff event"""
    print("\n" + "=" * 70)
    print("TEST 1: DROPOFF EVENT")
    print("=" * 70)
    
    video_path = find_video_file(DROPOFF_VIDEO)
    if not video_path:
        print(f"❌ Dropoff video not found. Please upload a video named:")
        print(f"   {TEST_VIDEOS_DIR}/{DROPOFF_VIDEO}")
        print(f"   Or any of: {DROPOFF_VIDEO.replace('.mp4', '.MOV')}, etc.")
        return None
    
    result = upload_video("/api/dropoff", video_path, "dropoff")
    
    if result:
        print(f"\n📋 Dropoff Event Details:")
        print(f"   Event ID: {result.get('event_id')}")
        print(f"   Person detected: {result.get('detections', {}).get('person_detected', False)}")
        print(f"   Cycle detected: {result.get('detections', {}).get('cycle_detected', False)}")
        return result.get('event_id')
    
    return None


def test_pickup_same_person(dropoff_event_id: str = None):
    """Test pickup event with same person"""
    print("\n" + "=" * 70)
    print("TEST 2: PICKUP EVENT (SAME PERSON)")
    print("=" * 70)
    
    video_path = find_video_file(PICKUP_SAME_VIDEO)
    if not video_path:
        print(f"❌ Pickup (same person) video not found. Please upload a video named:")
        print(f"   {TEST_VIDEOS_DIR}/{PICKUP_SAME_VIDEO}")
        return None
    
    result = upload_video("/api/pickup", video_path, "pickup (same person)")
    
    if result:
        match_result = result.get('match_result', {})
        print(f"\n📋 Pickup Event Details:")
        print(f"   Event ID: {result.get('event_id')}")
        print(f"   Same person: {match_result.get('is_same_person')}")
        print(f"   Similarity score: {match_result.get('similarity_score', 0):.3f}")
        print(f"   Confidence: {match_result.get('confidence', 'unknown')}")
        print(f"   Alert sent: {result.get('alert_sent', False)}")
        
        # Verify expected result
        if match_result.get('is_same_person'):
            print(f"\n   ✅ CORRECT: System correctly identified same person")
        else:
            print(f"\n   ⚠️  WARNING: System identified as different person (might be false negative)")
        
        return result.get('event_id')
    
    return None


def test_pickup_different_person(dropoff_event_id: str = None):
    """Test pickup event with different person"""
    print("\n" + "=" * 70)
    print("TEST 3: PICKUP EVENT (DIFFERENT PERSON)")
    print("=" * 70)
    
    video_path = find_video_file(PICKUP_DIFFERENT_VIDEO)
    if not video_path:
        print(f"❌ Pickup (different person) video not found. Please upload a video named:")
        print(f"   {TEST_VIDEOS_DIR}/{PICKUP_DIFFERENT_VIDEO}")
        return None
    
    result = upload_video("/api/pickup", video_path, "pickup (different person)")
    
    if result:
        match_result = result.get('match_result', {})
        print(f"\n📋 Pickup Event Details:")
        print(f"   Event ID: {result.get('event_id')}")
        print(f"   Same person: {match_result.get('is_same_person')}")
        print(f"   Similarity score: {match_result.get('similarity_score', 0):.3f}")
        print(f"   Confidence: {match_result.get('confidence', 'unknown')}")
        print(f"   Alert sent: {result.get('alert_sent', False)}")
        
        # Verify expected result
        if not match_result.get('is_same_person'):
            print(f"\n   ✅ CORRECT: System correctly identified different person")
            if result.get('alert_sent'):
                print(f"   🚨 ALERT: Security alert was sent successfully")
            else:
                print(f"   ⚠️  WARNING: Alert was not sent (check Telegram/Twilio configuration)")
        else:
            print(f"\n   ❌ ERROR: System incorrectly identified as same person (false positive)")
        
        return result.get('event_id')
    
    return None


def get_all_events():
    """Get all events from the database"""
    print("\n" + "=" * 70)
    print("EVENT HISTORY")
    print("=" * 70)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/events?limit=10", timeout=10)
        if response.status_code == 200:
            result = response.json()
            events = result.get('events', [])
            print(f"\n📊 Total events: {len(events)}")
            
            for event in events:
                event_type = event.get('event_type', 'unknown')
                event_id = event.get('event_id', 'unknown')
                timestamp = event.get('timestamp', 'unknown')
                match_result = event.get('match_result')
                alert_sent = event.get('alert_sent', False)
                
                print(f"\n   Event: {event_type.upper()}")
                print(f"   ID: {event_id}")
                print(f"   Time: {timestamp}")
                if match_result:
                    print(f"   Match: Same person = {match_result.get('is_same_person')}")
                    print(f"   Similarity: {match_result.get('similarity_score', 0):.3f}")
                if alert_sent:
                    print(f"   🚨 Alert sent")
        else:
            print(f"❌ Error retrieving events: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main test function"""
    print("=" * 70)
    print("CycleGuard AI - Video Testing")
    print("=" * 70)
    print()
    
    # Check if API is running
    if not check_api_health():
        return
    
    # Check if test videos directory exists
    if not os.path.exists(TEST_VIDEOS_DIR):
        print(f"\n⚠️  Test videos directory not found: {TEST_VIDEOS_DIR}")
        print(f"   Creating directory...")
        os.makedirs(TEST_VIDEOS_DIR, exist_ok=True)
        print(f"   ✅ Directory created. Please upload your test videos:")
        print(f"      - {DROPOFF_VIDEO}")
        print(f"      - {PICKUP_SAME_VIDEO}")
        print(f"      - {PICKUP_DIFFERENT_VIDEO}")
        return
    
    # Run tests
    dropoff_event_id = test_dropoff()
    
    if dropoff_event_id:
        time.sleep(2)  # Wait a bit between tests
        pickup_same_event_id = test_pickup_same_person(dropoff_event_id)
        
        if pickup_same_event_id:
            time.sleep(2)  # Wait a bit between tests
            pickup_different_event_id = test_pickup_different_person(dropoff_event_id)
    
    # Show event history
    get_all_events()
    
    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)
    print("\n💡 Tips:")
    print("   - Check the API logs for detailed processing information")
    print("   - Verify alerts were sent (if Telegram/Twilio is configured)")
    print("   - Review similarity scores to understand matching confidence")
    print("   - Adjust SIMILARITY_THRESHOLD in .env if needed")


if __name__ == "__main__":
    main()

