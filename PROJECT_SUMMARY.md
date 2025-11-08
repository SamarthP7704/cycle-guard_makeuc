# CycleGuard AI - Project Summary

## Overview
CycleGuard AI is an AI-powered surveillance system that detects who parked a cycle/escooter and alerts security if a different person attempts to move it. The system combines computer vision, person re-identification, and real-time alerting to provide campus security solutions.

## Architecture

### Components

1. **Object Detection Service** (`services/detection.py`)
   - Uses YOLOv8 for real-time object detection
   - Detects person and cycle/escooter in images/videos
   - Crops person region for further processing

2. **Person Re-identification Service** (`services/reid.py`)
   - Uses torchreid for appearance-based person matching
   - Extracts embeddings from person crops
   - Computes cosine similarity between embeddings
   - Fallback to simple feature extraction if model unavailable

3. **Database Service** (`services/database.py`)
   - Supabase integration for event storage
   - Stores dropoff and pickup events
   - Manages embeddings and match results

4. **Alert Service** (`services/alert.py`)
   - Telegram bot integration for instant alerts
   - Twilio SMS support (optional)
   - Sends security alerts for unauthorized pickup attempts

5. **Reka AI Service** (`services/reka_ai.py`)
   - Optional advanced vision analysis
   - Used for ambiguous cases (medium confidence matches)
   - Multimodal reasoning for better accuracy

### Workflow

#### Drop-off Event
1. Camera/image captures person parking cycle
2. YOLOv8 detects person and cycle
3. Person region is cropped
4. Torchreid extracts appearance embedding
5. Embedding and event data stored in database

#### Pickup Event
1. Camera/image captures person at station
2. YOLOv8 detects person and cycle
3. Person region is cropped
4. Torchreid extracts appearance embedding
5. Embedding compared with recent dropoff events
6. Cosine similarity computed
7. If similarity < threshold:
   - Reka AI used for verification (if ambiguous)
   - Security alert sent via Telegram/SMS
   - Event flagged as unauthorized

## Technology Stack

- **Backend**: FastAPI
- **Object Detection**: YOLOv8 (Ultralytics)
- **Person Re-ID**: Torchreid
- **Database**: Supabase (PostgreSQL)
- **Alerting**: Telegram Bot API, Twilio
- **Advanced AI**: Reka AI (optional)
- **Image Processing**: OpenCV, PIL
- **ML Framework**: PyTorch

## Key Features

1. **Real-time Detection**: Fast object detection using YOLOv8
2. **Person Matching**: Appearance-based re-identification
3. **Automatic Alerts**: Instant notifications for security threats
4. **Event Logging**: Complete audit trail of all events
5. **Flexible Integration**: RESTful API for easy integration
6. **Video Support**: Handles both images and video files
7. **Ambiguous Case Handling**: Reka AI for difficult cases

## API Endpoints

- `POST /api/dropoff` - Register drop-off event
- `POST /api/pickup` - Register pickup event
- `GET /api/events` - Get all events
- `GET /api/events/{event_id}` - Get specific event
- `GET /api/health` - Health check

## Database Schema

### Events Table
- `event_id` (UUID): Unique event identifier
- `event_type` (VARCHAR): 'dropoff' or 'pickup'
- `timestamp` (TIMESTAMP): Event timestamp
- `person_embedding` (JSONB): Person appearance embedding
- `person_bbox` (JSONB): Person bounding box
- `cycle_bbox` (JSONB): Cycle bounding box (optional)
- `image_path` (TEXT): Path to event image
- `match_result` (JSONB): Match result for pickup events
- `alert_sent` (BOOLEAN): Whether alert was sent

## Configuration

Environment variables in `.env`:
- `SUPABASE_URL`: Supabase project URL (required)
- `SUPABASE_KEY`: Supabase API key (required)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token (optional)
- `TELEGRAM_CHAT_ID`: Telegram chat ID (optional)
- `TWILIO_ACCOUNT_SID`: Twilio account SID (optional)
- `TWILIO_AUTH_TOKEN`: Twilio auth token (optional)
- `TWILIO_PHONE_NUMBER`: Twilio phone number (optional)
- `REKA_API_KEY`: Reka AI API key (optional)
- `SIMILARITY_THRESHOLD`: Similarity threshold (default: 0.7)

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Set up Database**
   - Create Supabase project
   - Run `database/schema.sql` in SQL Editor

4. **Run Application**
   ```bash
   uvicorn main:app --reload
   ```

## Testing

Use the test client:
```bash
python test_client.py dropoff_image.jpg pickup_image.jpg
```

## Future Enhancements

1. **Real-time Video Streaming**: Process live video feeds
2. **Multiple Camera Support**: Handle multiple surveillance cameras
3. **Mobile App**: Native mobile app for alerts
4. **Dashboard**: Web dashboard for monitoring
5. **Advanced Analytics**: Statistical analysis of events
6. **Face Recognition**: Additional face-based verification
7. **Cloud Storage**: Store images in cloud storage (S3, etc.)
8. **Webhook Support**: Send events to external systems

## Performance Considerations

- YOLOv8 model loads on startup (can be optimized with model caching)
- Embedding extraction takes ~100-200ms per image
- Database queries are indexed for fast retrieval
- Image processing is optimized with OpenCV

## Security Considerations

- API endpoints should be protected with authentication
- Images stored locally (consider cloud storage for production)
- Database access controlled via Supabase RLS policies
- Alert credentials stored securely in environment variables

## License

MIT License

