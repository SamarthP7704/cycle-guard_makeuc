# CycleGuard AI 🚲🛡️

An AI-powered surveillance system that detects who parked a cycle/escooter and alerts security if a different person attempts to move it.

## Features

- **Object Detection**: YOLOv8 detects person and cycle/escooter in real-time
- **Person Re-identification**: Torchreid extracts appearance embeddings for person matching
- **Identity Verification**: Cosine similarity comparison to verify if pickup person matches drop-off person
- **Real-time Alerts**: Telegram bot integration for instant notifications
- **Database Logging**: Supabase integration for event tracking and history
- **API**: FastAPI backend for easy integration

## Tech Stack

- **Object Detection**: YOLOv8 / OpenCV
- **Person Re-ID**: Torchreid
- **Backend**: FastAPI
- **Database**: Supabase
- **Alerting**: Telegram Bot / Twilio
- **Optional**: Reka AI for ambiguous cases (works without it)

## Quick Start

### Option 1: Automated Setup
```bash
python setup.py
```

### Option 2: Manual Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file:**
```bash
cp .env.example .env
# Then edit .env with your credentials
```

3. **Set up Supabase database:**
   - Create a new Supabase project at https://supabase.com
   - Go to SQL Editor and run the script in `database/schema.sql`
   - Copy your Supabase URL and anon key to `.env`

4. **Set up Telegram Bot (optional):**
   - Create a bot using @BotFather on Telegram
   - Get your bot token and chat ID
   - Add them to `.env`

5. **Run the application:**
```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script
./run.sh

# Or run directly
python main.py
```

## Environment Variables

Required:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/service key

Optional:
- `TELEGRAM_BOT_TOKEN`: Telegram bot token for alerts
- `TELEGRAM_CHAT_ID`: Telegram chat ID to send alerts to
- `TWILIO_ACCOUNT_SID`: Twilio account SID for SMS alerts
- `TWILIO_AUTH_TOKEN`: Twilio auth token
- `TWILIO_PHONE_NUMBER`: Twilio phone number
- `REKA_API_KEY`: Reka AI API key for advanced analysis
- `SIMILARITY_THRESHOLD`: Similarity threshold (default: 0.7)

## API Endpoints

### POST /api/dropoff
Register a drop-off event (person parks cycle/escooter)

**Request**: Multipart form data with image/video file

**Response**:
```json
{
  "event_id": "uuid",
  "status": "success",
  "person_embedding_id": "uuid",
  "message": "Drop-off event recorded"
}
```

### POST /api/pickup
Register a pickup event (person attempts to pick up cycle/escooter)

**Request**: Multipart form data with image/video file

**Response**:
```json
{
  "event_id": "uuid",
  "status": "success",
  "match_result": {
    "is_same_person": true/false,
    "similarity_score": 0.85,
    "confidence": "high"
  },
  "alert_sent": true/false
}
```

### GET /api/events
Get all events with pagination

### GET /api/events/{event_id}
Get specific event details

## Usage

### Video Testing

1. **Upload test videos** to `test_videos/` folder:
   - `dropoff_video.mp4` - Person dropping off scooter
   - `pickup_same_person.mp4` - Same person picking up
   - `pickup_different_person.mp4` - Different person picking up

2. **Run test script**:
   ```bash
   python test_video_flow.py
   ```

### API Usage

1. **Drop-off Event**: Send image/video when someone parks a cycle
2. **Pickup Event**: Send image/video when someone attempts to pick up
3. **Automatic Alert**: System compares embeddings and alerts if different person

See [TESTING.md](TESTING.md) for detailed testing instructions.

## Project Structure

```
cycle_guard/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── models/                # Database models
│   ├── __init__.py
│   └── event.py
├── services/              # Business logic
│   ├── __init__.py
│   ├── detection.py       # YOLOv8 object detection
│   ├── reid.py           # Torchreid person re-identification
│   ├── database.py       # Supabase database operations
│   └── alert.py          # Telegram/Twilio alerting
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── image_processing.py
├── database/              # Database schemas
│   └── schema.sql
└── requirements.txt
```

## License

MIT License

