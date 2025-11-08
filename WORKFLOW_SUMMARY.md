# CycleGuard AI - Workflow Summary (Quick Reference)

## 🎬 Complete Video Processing Pipeline

### DROP-OFF EVENT (Parking)

```
1. Video Upload (drop-off.mp4)
   ↓
2. Extract Middle Frame (OpenCV)
   ↓
3. Detect Person + Cycle (YOLOv8)
   ↓
4. Crop Person Region
   ↓
5. Extract Person Embedding (Torchreid or Fallback)
   ↓
6. Store in Database (Supabase)
   ↓
7. Return Event ID
```

### PICKUP EVENT (Picking Up)

```
1. Video Upload (pickup.mp4)
   ↓
2. Extract Middle Frame (OpenCV)
   ↓
3. Detect Person + Cycle (YOLOv8)
   ↓
4. Crop Person Region
   ↓
5. Extract Person Embedding (Torchreid or Fallback)
   ↓
6. Query Database for Recent Dropoffs
   ↓
7. Compare Embeddings (Cosine Similarity)
   ↓
8. Reka AI Verification (if ambiguous & configured)
   ↓
9. Determine Match Result
   ↓
10. Send Alert (if different person)
   ↓
11. Update Database
   ↓
12. Return Match Result
```

---

## 🔧 Technologies Used

| Step | Technology | Library/API | Purpose |
|------|------------|-------------|---------|
| **Upload** | FastAPI | `fastapi` | Web framework |
| **File Save** | Async I/O | `aiofiles` | Save uploaded file |
| **Frame Extract** | OpenCV | `cv2` | Extract frame from video |
| **Object Detection** | YOLOv8 | `ultralytics` | Detect person & cycle |
| **Person Crop** | NumPy | `numpy` | Crop person region |
| **Embedding** | Torchreid | `torchreid` | Extract person features |
| **Fallback** | OpenCV | `cv2` | Color histograms + texture |
| **Similarity** | NumPy | `numpy` | Cosine similarity |
| **Database** | Supabase | `supabase` | PostgreSQL database |
| **Reka AI** | Reka API | `requests` | Advanced verification |
| **Alerts** | Telegram | `requests` | Send alerts |
| **Alerts** | Twilio | `twilio` | SMS alerts |

---

## 📊 Functions Called (In Order)

### Drop-off Event

```python
1. register_dropoff(file)
   ├─ save_uploaded_file(file)
   ├─ extract_frame_from_video(file_path)
   ├─ validate_image(image)
   ├─ detection_service.detect_objects(image)
   ├─ detection_service.detect_and_crop_person(image)
   ├─ reid_service.extract_embedding(person_crop)
   ├─ db_service.create_event(event_data)
   └─ return JSONResponse
```

### Pickup Event

```python
1. register_pickup(file)
   ├─ save_uploaded_file(file)
   ├─ extract_frame_from_video(file_path)
   ├─ validate_image(image)
   ├─ detection_service.detect_objects(image)
   ├─ detection_service.detect_and_crop_person(image)
   ├─ reid_service.extract_embedding(person_crop)
   ├─ db_service.get_recent_dropoff_events(limit=10)
   ├─ reid_service.compute_similarity(emb1, emb2)  # For each dropoff
   ├─ reka_service.analyze_person_similarity(...)  # If ambiguous
   ├─ alert_service.send_security_alert(...)  # If different person
   ├─ db_service.create_event(event_data)
   ├─ db_service.update_event_match_result(...)
   └─ return JSONResponse
```

---

## 🎯 Key Processing Steps

### 1. Video → Frame
- **Function**: `extract_frame_from_video()`
- **Technology**: OpenCV
- **Process**: Extract middle frame (better for detection)
- **Output**: NumPy array (image)

### 2. Frame → Detections
- **Function**: `detect_objects()`
- **Technology**: YOLOv8
- **Process**: Detect person (class 0) and cycle (classes 1,2,3)
- **Output**: Bounding boxes `[x1, y1, x2, y2]`

### 3. Detections → Person Crop
- **Function**: `detect_and_crop_person()`
- **Technology**: NumPy array slicing
- **Process**: Extract person region using bounding box
- **Output**: Cropped person image

### 4. Person Crop → Embedding
- **Function**: `extract_embedding()`
- **Technology**: Torchreid (or fallback)
- **Process**: 
  - **Torchreid**: Deep learning model → feature vector
  - **Fallback**: Color histograms + texture → feature vector
- **Output**: Embedding vector (512-2048 dimensions)

### 5. Embeddings → Similarity
- **Function**: `compute_similarity()`
- **Technology**: NumPy (cosine similarity)
- **Process**: 
  - Normalize embeddings
  - Compute dot product
  - Normalize to [0, 1] range
- **Output**: Similarity score (0.0 - 1.0)

### 6. Similarity → Match Result
- **Function**: Comparison logic
- **Process**:
  - If similarity >= 0.7 → Same person
  - If similarity 0.6-0.7 → Ambiguous → Reka AI (if configured)
  - If similarity < 0.7 → Different person → Alert
- **Output**: Match result (is_same_person, confidence)

---

## 📡 External APIs Called

### 1. Reka AI API (Optional)
- **Endpoint**: `https://api.reka.ai/v1/chat`
- **Method**: POST
- **When**: Ambiguous cases (similarity 0.6-0.7)
- **Payload**: Two images (base64) + prompt
- **Response**: Yes/No + confidence score

### 2. Telegram Bot API (Optional)
- **Endpoint**: `https://api.telegram.org/bot{token}/sendPhoto`
- **Method**: POST
- **When**: Different person detected
- **Payload**: Image file + message
- **Response**: Success/failure

### 3. Twilio API (Optional)
- **Endpoint**: `https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json`
- **Method**: POST
- **When**: Different person detected
- **Payload**: Phone number + message
- **Response**: Message SID

### 4. Supabase API (Database)
- **Endpoint**: `{supabase_url}/rest/v1/events`
- **Method**: POST, GET, PATCH
- **When**: Always (if configured)
- **Payload**: Event data (JSON)
- **Response**: Database records

---

## 🔄 Data Flow

```
VIDEO FILE
    │
    ├─→ [OpenCV] → FRAME (NumPy array)
    │
    ├─→ [YOLOv8] → DETECTIONS (Bounding boxes)
    │
    ├─→ [NumPy] → PERSON CROP (Image)
    │
    ├─→ [Torchreid] → EMBEDDING (Vector)
    │
    ├─→ [Supabase] → DATABASE (Storage)
    │
    ├─→ [NumPy] → SIMILARITY (Score)
    │
    ├─→ [Reka AI] → VERIFICATION (Optional)
    │
    └─→ [Telegram] → ALERT (If different person)
```

---

## 📝 Response Format

### Drop-off Response
```json
{
  "event_id": "uuid",
  "status": "success",
  "person_embedding_id": "uuid",
  "message": "Drop-off event recorded successfully",
  "detections": {
    "person_detected": true,
    "cycle_detected": false
  }
}
```

### Pickup Response
```json
{
  "event_id": "uuid",
  "status": "success",
  "match_result": {
    "is_same_person": false,
    "similarity_score": 0.45,
    "confidence": "low",
    "matched_event_id": "uuid"
  },
  "alert_sent": true,
  "message": "Pickup event processed successfully",
  "detections": {
    "person_detected": true,
    "cycle_detected": true
  }
}
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
SUPABASE_URL=...          # Database URL
SUPABASE_KEY=...          # Database key
TELEGRAM_BOT_TOKEN=...    # Telegram bot token
TELEGRAM_CHAT_ID=...      # Telegram chat ID
TWILIO_ACCOUNT_SID=...    # Twilio account SID
TWILIO_AUTH_TOKEN=...     # Twilio auth token
TWILIO_PHONE_NUMBER=...   # Twilio phone number
REKA_API_KEY=...          # Reka AI API key (optional)
SIMILARITY_THRESHOLD=0.7  # Similarity threshold
```

---

## 🚀 Performance

- **Video Processing**: 2-5 seconds
- **Object Detection**: 0.5-1 second
- **Embedding Extraction**: 0.5-2 seconds
- **Similarity Comparison**: <0.1 seconds
- **Database Query**: 0.1-0.5 seconds
- **Total Time**: 3-8 seconds per video

---

## 🎓 Summary

**Input**: Video file (MP4, MOV, AVI, etc.)

**Processing**:
1. Extract frame → Detect objects → Crop person → Extract embedding
2. Compare embeddings → Determine match → Send alert (if needed)

**Output**: 
- Event ID
- Match result (same/different person)
- Similarity score
- Alert status

**Technologies**: YOLOv8, Torchreid, OpenCV, NumPy, Supabase, Telegram, Reka AI

**Result**: Security system that detects unauthorized cycle pickups!

