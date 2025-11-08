from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import cv2
import numpy as np
import os
import uuid
from datetime import datetime

from config import settings
from services.detection import DetectionService
from services.reid import ReIDService
from services.database import DatabaseService
from services.alert import AlertService
from services.reka_ai import RekaAIService
from models.event import EventType, MatchResult
from utils.image_processing import (
    extract_frame_from_video,
    validate_image,
    load_image,
    save_uploaded_file
)

app = FastAPI(
    title="CycleGuard AI",
    description="AI-powered surveillance system for cycle/escooter security",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
detection_service = DetectionService()
reid_service = ReIDService()
db_service = DatabaseService()
alert_service = AlertService()
reka_service = RekaAIService()

# Create uploads directory
os.makedirs("uploads", exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CycleGuard AI API",
        "version": "1.0.0",
        "endpoints": {
            "dropoff": "/api/dropoff",
            "pickup": "/api/pickup",
            "events": "/api/events",
            "event_detail": "/api/events/{event_id}"
        }
    }


@app.post("/api/dropoff")
async def register_dropoff(file: UploadFile = File(...)):
    """
    Register a drop-off event (person parks cycle/escooter)
    
    Accepts image or video file
    """
    try:
        # Save uploaded file
        file_path = await save_uploaded_file(file)
        
        # Load image (handle video if needed)
        # Check file extension as content_type might not be reliable
        file_ext = os.path.splitext(file_path)[1].lower()
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        
        if file.content_type and file.content_type.startswith("video/") or file_ext in video_extensions:
            # Extract middle frame from video for better detection
            image = extract_frame_from_video(file_path, frame_index=None)
        else:
            image = load_image(file_path)
        
        if not validate_image(image):
            raise HTTPException(status_code=400, detail="Invalid image or video")
        
        # Detect person and cycle
        detections = detection_service.detect_objects(image)
        
        if detections['person'] is None:
            raise HTTPException(
                status_code=400,
                detail="No person detected in image/video. Please ensure a person is clearly visible."
            )
        
        # Crop person and extract embedding
        person_crop, person_bbox = detection_service.detect_and_crop_person(image)
        
        if person_crop is None:
            raise HTTPException(
                status_code=400,
                detail="Could not crop person from image/video"
            )
        
        # Extract person embedding
        person_embedding = reid_service.extract_embedding(person_crop)
        
        # Create event
        event_data = {
            "event_type": EventType.DROPOFF.value,
            "person_embedding": person_embedding.tolist(),
            "person_bbox": person_bbox,
            "cycle_bbox": detections.get('cycle'),
            "image_path": file_path
        }
        
        event_id = db_service.create_event(event_data)
        
        return JSONResponse(
            status_code=200,
            content={
                "event_id": event_id,
                "status": "success",
                "person_embedding_id": event_id,
                "message": "Drop-off event recorded successfully",
                "detections": {
                    "person_detected": detections['person'] is not None,
                    "cycle_detected": detections['cycle'] is not None
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing dropoff: {str(e)}")


@app.post("/api/pickup")
async def register_pickup(file: UploadFile = File(...)):
    """
    Register a pickup event (person attempts to pick up cycle/escooter)
    
    Compares with recent dropoff events and sends alert if different person
    """
    try:
        # Save uploaded file
        file_path = await save_uploaded_file(file)
        
        # Load image (handle video if needed)
        # Check file extension as content_type might not be reliable
        file_ext = os.path.splitext(file_path)[1].lower()
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        
        if file.content_type and file.content_type.startswith("video/") or file_ext in video_extensions:
            # Extract middle frame from video for better detection
            image = extract_frame_from_video(file_path, frame_index=None)
        else:
            image = load_image(file_path)
        
        if not validate_image(image):
            raise HTTPException(status_code=400, detail="Invalid image or video")
        
        # Detect person and cycle
        detections = detection_service.detect_objects(image)
        
        if detections['person'] is None:
            raise HTTPException(
                status_code=400,
                detail="No person detected in image/video. Please ensure a person is clearly visible."
            )
        
        # Crop person and extract embedding
        person_crop, person_bbox = detection_service.detect_and_crop_person(image)
        
        if person_crop is None:
            raise HTTPException(
                status_code=400,
                detail="Could not crop person from image/video"
            )
        
        # Extract person embedding
        pickup_embedding = reid_service.extract_embedding(person_crop)
        
        # Get recent dropoff events for comparison
        dropoff_events = db_service.get_recent_dropoff_events(limit=10)
        
        if not dropoff_events:
            # No dropoff events to compare with
            match_result = MatchResult(
                is_same_person=False,
                similarity_score=0.0,
                confidence="low",
                matched_event_id=None
            )
        else:
            # Compare with all dropoff events and find best match
            best_similarity = 0.0
            best_match_event_id = None
            
            for dropoff_event in dropoff_events:
                dropoff_embedding = np.array(dropoff_event['person_embedding'])
                similarity = reid_service.compute_similarity(pickup_embedding, dropoff_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_event_id = dropoff_event['event_id']
            
            # Determine if same person based on threshold
            is_same_person = best_similarity >= settings.similarity_threshold
            
            # Determine confidence
            if best_similarity >= 0.8:
                confidence = "high"
            elif best_similarity >= 0.6:
                confidence = "medium"
            else:
                confidence = "low"
            
            # Use Reka AI for ambiguous cases (medium confidence or near threshold)
            # Only if Reka AI is configured and available
            use_reka = False
            if reka_service.is_configured() and (confidence == "medium" or (0.6 <= best_similarity < 0.75)):
                # Get the full matched dropoff event from database to access image_path
                matched_event = db_service.get_event(best_match_event_id)
                if matched_event and matched_event.get('image_path'):
                    try:
                        dropoff_image = load_image(matched_event['image_path'])
                        # Get person crop from dropoff image
                        dropoff_person_crop, _ = detection_service.detect_and_crop_person(dropoff_image)
                        
                        if dropoff_person_crop is not None:
                            # Convert to bytes for Reka AI
                            import cv2
                            _, dropoff_buffer = cv2.imencode('.jpg', dropoff_person_crop)
                            _, pickup_buffer = cv2.imencode('.jpg', person_crop)
                            
                            # Call Reka AI
                            reka_result = reka_service.analyze_person_similarity(
                                dropoff_buffer.tobytes(),
                                pickup_buffer.tobytes()
                            )
                            
                            if reka_result:
                                use_reka = True
                                # Override with Reka AI result if confidence is higher
                                if reka_result['confidence'] > 0.7:
                                    is_same_person = reka_result['is_same_person']
                                    confidence = "high" if reka_result['confidence'] > 0.8 else "medium"
                                    best_similarity = reka_result['confidence']  # Update similarity with Reka confidence
                    except Exception as e:
                        print(f"Error using Reka AI: {e}")
                        # Continue with torchreid result (graceful fallback)
            
            match_result = MatchResult(
                is_same_person=is_same_person,
                similarity_score=best_similarity,
                confidence=confidence,
                matched_event_id=best_match_event_id
            )
        
        # Create pickup event
        event_data = {
            "event_type": EventType.PICKUP.value,
            "person_embedding": pickup_embedding.tolist(),
            "person_bbox": person_bbox,
            "cycle_bbox": detections.get('cycle'),
            "image_path": file_path
        }
        
        event_id = db_service.create_event(event_data)
        
        # Update event with match result
        alert_sent = False
        if not match_result.is_same_person:
            # Send alert for unauthorized pickup
            alert_sent = alert_service.send_security_alert(
                event_id=event_id,
                similarity_score=match_result.similarity_score,
                image_path=file_path
            )
        
        db_service.update_event_match_result(event_id, match_result, alert_sent)
        
        return JSONResponse(
            status_code=200,
            content={
                "event_id": event_id,
                "status": "success",
                "match_result": {
                    "is_same_person": match_result.is_same_person,
                    "similarity_score": match_result.similarity_score,
                    "confidence": match_result.confidence,
                    "matched_event_id": match_result.matched_event_id
                },
                "alert_sent": alert_sent,
                "message": "Pickup event processed successfully",
                "detections": {
                    "person_detected": detections['person'] is not None,
                    "cycle_detected": detections['cycle'] is not None
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing pickup: {str(e)}")


@app.get("/api/events")
async def get_events(limit: int = 100, offset: int = 0):
    """Get all events with pagination"""
    try:
        events = db_service.get_all_events(limit=limit, offset=offset)
        return JSONResponse(
            status_code=200,
            content={
                "events": events,
                "count": len(events),
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    """Get specific event by ID"""
    try:
        event = db_service.get_event(event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        return JSONResponse(status_code=200, content=event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching event: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "detection": "ready",
            "reid": "ready",
            "database": "ready",
            "alert": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

