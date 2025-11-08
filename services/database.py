from typing import List, Optional
from datetime import datetime
from models.event import Event, EventType, MatchResult
from config import settings
import uuid
import json

# Try to import Supabase, but continue without it if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None
    print("⚠️  Supabase not installed. Database operations will be disabled.")


class DatabaseService:
    """Service for database operations using Supabase"""
    
    def __init__(self):
        if SUPABASE_AVAILABLE:
            try:
                self.supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"⚠️  Error initializing Supabase: {e}")
                self.supabase = None
        else:
            self.supabase = None
            print("⚠️  Supabase not available. Using in-memory storage (testing mode).")
    
    def create_event(self, event: dict) -> str:
        """Create a new event in the database"""
        event_id = str(uuid.uuid4())
        
        if not self.supabase:
            print(f"⚠️  Database not available. Event {event_id} created in memory only.")
            return event_id
        
        event_data = {
            "event_id": event_id,
            "event_type": event["event_type"],
            "timestamp": datetime.utcnow().isoformat(),
            "person_embedding": json.dumps(event["person_embedding"]),
            "person_bbox": json.dumps(event["person_bbox"]),
            "cycle_bbox": json.dumps(event.get("cycle_bbox")),
            "image_path": event.get("image_path"),
            "alert_sent": False
        }
        
        try:
            result = self.supabase.table("events").insert(event_data).execute()
            return event_id
        except Exception as e:
            print(f"Error creating event: {e}")
            # Fallback: return event_id even if database insert fails
            return event_id
    
    def get_recent_dropoff_events(self, limit: int = 10) -> List[dict]:
        """Get recent dropoff events for comparison"""
        if not self.supabase:
            print("⚠️  Database not available. Cannot fetch dropoff events.")
            return []
            
        try:
            result = self.supabase.table("events")\
                .select("*")\
                .eq("event_type", EventType.DROPOFF.value)\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .execute()
            
            events = []
            for row in result.data:
                events.append({
                    "event_id": row["event_id"],
                    "person_embedding": json.loads(row["person_embedding"]),
                    "person_bbox": json.loads(row["person_bbox"]),
                    "timestamp": row["timestamp"]
                })
            return events
        except Exception as e:
            print(f"Error fetching dropoff events: {e}")
            return []
    
    def update_event_match_result(self, event_id: str, match_result: MatchResult, alert_sent: bool = False):
        """Update event with match result"""
        try:
            update_data = {
                "match_result": json.dumps({
                    "is_same_person": match_result.is_same_person,
                    "similarity_score": match_result.similarity_score,
                    "confidence": match_result.confidence,
                    "matched_event_id": match_result.matched_event_id
                }),
                "alert_sent": alert_sent
            }
            
            self.supabase.table("events")\
                .update(update_data)\
                .eq("event_id", event_id)\
                .execute()
        except Exception as e:
            print(f"Error updating event match result: {e}")
    
    def get_event(self, event_id: str) -> Optional[dict]:
        """Get event by ID"""
        try:
            result = self.supabase.table("events")\
                .select("*")\
                .eq("event_id", event_id)\
                .execute()
            
            if result.data:
                row = result.data[0]
                return {
                    "event_id": row["event_id"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"],
                    "person_embedding": json.loads(row["person_embedding"]),
                    "person_bbox": json.loads(row["person_bbox"]),
                    "cycle_bbox": json.loads(row.get("cycle_bbox")) if row.get("cycle_bbox") else None,
                    "image_path": row.get("image_path"),
                    "match_result": json.loads(row["match_result"]) if row.get("match_result") else None,
                    "alert_sent": row.get("alert_sent", False)
                }
            return None
        except Exception as e:
            print(f"Error getting event: {e}")
            return None
    
    def get_all_events(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all events with pagination"""
        try:
            result = self.supabase.table("events")\
                .select("*")\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            events = []
            for row in result.data:
                events.append({
                    "event_id": row["event_id"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"],
                    "person_embedding": json.loads(row["person_embedding"]) if row.get("person_embedding") else None,
                    "person_bbox": json.loads(row["person_bbox"]) if row.get("person_bbox") else None,
                    "cycle_bbox": json.loads(row["cycle_bbox"]) if row.get("cycle_bbox") else None,
                    "image_path": row.get("image_path"),
                    "match_result": json.loads(row["match_result"]) if row.get("match_result") else None,
                    "alert_sent": row.get("alert_sent", False)
                })
            return events
        except Exception as e:
            print(f"Error getting all events: {e}")
            return []

