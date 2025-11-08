"""
Direct video testing script - tests detection and ReID without API server
This allows testing the core functionality without Supabase setup
"""
import cv2
import numpy as np
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from services.detection import DetectionService
from services.reid import ReIDService
from utils.image_processing import extract_frame_from_video, validate_image


def test_video_processing(video_path: str, video_name: str):
    """Test video processing for a single video"""
    print(f"\n{'='*70}")
    print(f"Testing: {video_name}")
    print(f"{'='*70}")
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return None, None
    
    print(f"📹 Video: {os.path.basename(video_path)}")
    print(f"   Size: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")
    
    try:
        # Extract frame from video
        print("   ⏳ Extracting frame from video...")
        image = extract_frame_from_video(video_path, frame_index=None)
        print(f"   ✅ Frame extracted: {image.shape[1]}x{image.shape[0]}")
        
        # Initialize services
        print("   ⏳ Initializing detection service...")
        detection_service = DetectionService()
        print("   ✅ Detection service ready")
        
        # Detect objects
        print("   ⏳ Detecting person and cycle...")
        detections = detection_service.detect_objects(image)
        
        person_detected = detections['person'] is not None
        cycle_detected = detections['cycle'] is not None
        
        print(f"   ✅ Person detected: {person_detected}")
        print(f"   ✅ Cycle detected: {cycle_detected}")
        
        if not person_detected:
            print("   ⚠️  WARNING: No person detected in video!")
            return None, None
        
        # Crop person and extract embedding
        print("   ⏳ Extracting person embedding...")
        person_crop, person_bbox = detection_service.detect_and_crop_person(image)
        
        if person_crop is None:
            print("   ❌ Could not crop person from image")
            return None, None
        
        print(f"   ✅ Person cropped: {person_crop.shape[1]}x{person_crop.shape[0]}")
        print(f"   ✅ Bounding box: {person_bbox}")
        
        # Initialize ReID service
        print("   ⏳ Initializing ReID service...")
        reid_service = ReIDService()
        print("   ✅ ReID service ready")
        
        # Extract embedding
        print("   ⏳ Computing person embedding...")
        embedding = reid_service.extract_embedding(person_crop)
        print(f"   ✅ Embedding extracted: {len(embedding)} dimensions")
        print(f"   ✅ Embedding norm: {np.linalg.norm(embedding):.3f}")
        
        return embedding, person_bbox
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def compare_embeddings(embedding1, embedding2, name1: str, name2: str):
    """Compare two embeddings and compute similarity"""
    if embedding1 is None or embedding2 is None:
        print(f"\n❌ Cannot compare: Missing embeddings")
        return None
    
    print(f"\n{'='*70}")
    print(f"Comparing: {name1} vs {name2}")
    print(f"{'='*70}")
    
    reid_service = ReIDService()
    similarity = reid_service.compute_similarity(embedding1, embedding2)
    
    print(f"   Similarity score: {similarity:.3f}")
    
    # Determine if same person (threshold = 0.85 for better accuracy with torchreid)
    threshold = 0.85
    is_same_person = similarity >= threshold
    
    if similarity >= 0.8:
        confidence = "high"
    elif similarity >= 0.6:
        confidence = "medium"
    else:
        confidence = "low"
    
    print(f"   Is same person: {is_same_person} (threshold: {threshold})")
    print(f"   Confidence: {confidence}")
    
    if is_same_person:
        print(f"   ✅ MATCH: Same person detected")
    else:
        print(f"   🚨 ALERT: Different person detected")
    
    return {
        'similarity': similarity,
        'is_same_person': is_same_person,
        'confidence': confidence
    }


def main():
    """Main test function"""
    print("="*70)
    print("CycleGuard AI - Direct Video Testing")
    print("="*70)
    print("\nThis script tests video processing without API server")
    print("Testing: Detection, Person Re-ID, and Similarity Comparison")
    print()
    
    test_videos_dir = "test_videos"
    
    # Video files
    dropoff_video = os.path.join(test_videos_dir, "drop-off.mp4")
    pickup_video = os.path.join(test_videos_dir, "pickup.mp4")
    steal_video = os.path.join(test_videos_dir, "steal.mp4")
    
    # Test dropoff video
    print("\n" + "="*70)
    print("STEP 1: Processing Drop-off Video")
    print("="*70)
    dropoff_embedding, dropoff_bbox = test_video_processing(dropoff_video, "Drop-off")
    
    if dropoff_embedding is None:
        print("\n❌ Failed to process dropoff video. Cannot continue.")
        return
    
    # Test pickup video (should be same person)
    print("\n" + "="*70)
    print("STEP 2: Processing Pickup Video (Expected: Same Person)")
    print("="*70)
    pickup_embedding, pickup_bbox = test_video_processing(pickup_video, "Pickup (Same Person)")
    
    if pickup_embedding is not None:
        # Compare dropoff vs pickup
        result1 = compare_embeddings(
            dropoff_embedding, 
            pickup_embedding,
            "Drop-off",
            "Pickup (Same Person)"
        )
    
    # Test steal video (should be different person)
    print("\n" + "="*70)
    print("STEP 3: Processing Steal Video (Expected: Different Person)")
    print("="*70)
    steal_embedding, steal_bbox = test_video_processing(steal_video, "Steal (Different Person)")
    
    if steal_embedding is not None:
        # Compare dropoff vs steal
        result2 = compare_embeddings(
            dropoff_embedding,
            steal_embedding,
            "Drop-off",
            "Steal (Different Person)"
        )
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if dropoff_embedding is not None:
        print("✅ Drop-off video processed successfully")
    else:
        print("❌ Drop-off video failed")
    
    if pickup_embedding is not None:
        if result1 and result1['is_same_person']:
            print("✅ Pickup video: Correctly identified as SAME person")
        else:
            print("⚠️  Pickup video: Identified as different person (might be incorrect)")
    else:
        print("❌ Pickup video failed")
    
    if steal_embedding is not None:
        if result2 and not result2['is_same_person']:
            print("✅ Steal video: Correctly identified as DIFFERENT person")
        else:
            print("⚠️  Steal video: Identified as same person (FALSE POSITIVE!)")
    else:
        print("❌ Steal video failed")
    
    print("\n" + "="*70)
    print("Testing Complete!")
    print("="*70)


if __name__ == "__main__":
    main()

