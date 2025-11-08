# CycleGuard AI - Complete System Workflow Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Complete Workflow](#complete-workflow)
4. [Detailed Step-by-Step Process](#detailed-step-by-step-process)
5. [APIs and Functions Used](#apis-and-functions-used)
6. [Data Flow Diagram](#data-flow-diagram)

---

## System Overview

CycleGuard AI is an AI-powered surveillance system that:
1. **Detects** when someone parks a cycle/escooter (drop-off event)
2. **Tracks** who parked it using person re-identification
3. **Monitors** when someone attempts to pick it up
4. **Compares** the pickup person with the drop-off person
5. **Alerts** security if a different person tries to pick up the cycle

---

## Technology Stack

### Core Technologies
- **FastAPI**: Web framework for REST API
- **YOLOv8 (Ultralytics)**: Object detection (person, cycle)
- **Torchreid**: Person re-identification (deep learning)
- **OpenCV**: Image/video processing
- **NumPy**: Numerical computations
- **PyTorch**: Deep learning framework
- **Supabase**: PostgreSQL database (cloud)
- **Telegram Bot API**: Alerting system
- **Twilio**: SMS alerts (optional)
- **Reka AI**: Advanced vision analysis (optional)

### Python Libraries
- `ultralytics`: YOLOv8 model
- `torchreid`: Person re-ID models
- `opencv-python`: Computer vision
- `numpy`: Array operations
- `supabase`: Database client
- `requests`: HTTP requests
- `aiofiles`: Async file operations

---

## Complete Workflow

### Two Main Scenarios

#### Scenario 1: Drop-off Event (Parking)
```
Video Upload → Frame Extraction → Object Detection → Person Crop → 
Embedding Extraction → Database Storage → Response
```

#### Scenario 2: Pickup Event (Picking Up)
```
Video Upload → Frame Extraction → Object Detection → Person Crop → 
Embedding Extraction → Database Query → Similarity Comparison → 
Reka AI (if ambiguous) → Alert (if different person) → Database Update → Response
```

---

## Detailed Step-by-Step Process

### 📥 **STEP 1: Video/Image Upload**

**API Endpoint**: `POST /api/dropoff` or `POST /api/pickup`

**Function**: `register_dropoff()` or `register_pickup()` in `main.py`

**Process**:
1. Client sends HTTP POST request with video/image file
2. FastAPI receives file as `UploadFile` object
3. File is saved to disk using `save_uploaded_file()`

**Code Location**: `main.py:74-75`
```python
file_path = await save_uploaded_file(file)
```

**Function Used**: `utils/image_processing.py:save_uploaded_file()`
- Uses `aiofiles` for async file writing
- Saves to `uploads/` directory
- Returns file path

---

### 🎬 **STEP 2: Video Frame Extraction**

**Function**: `extract_frame_from_video()` in `utils/image_processing.py`

**Process**:
1. Check if file is video (by extension: .mp4, .mov, .avi, .mkv, .webm)
2. Open video using OpenCV's `VideoCapture`
3. Get total frame count
4. Extract **middle frame** (better for person detection)
5. If middle frame fails, fallback to first frame
6. Return frame as NumPy array

**Code Location**: `main.py:82-84`
```python
if file_ext in video_extensions:
    image = extract_frame_from_video(file_path, frame_index=None)
```

**Technologies**:
- **OpenCV (`cv2`)**: Video processing
- **NumPy**: Image array representation

**Function Details**:
```python
# utils/image_processing.py:19-63
def extract_frame_from_video(video_path, frame_index=None):
    cap = cv2.VideoCapture(video_path)  # Open video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Get frame count
    frame_index = total_frames // 2  # Middle frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)  # Seek to frame
    ret, frame = cap.read()  # Read frame
    return frame  # Return as NumPy array
```

---

### 🖼️ **STEP 3: Image Validation**

**Function**: `validate_image()` in `utils/image_processing.py`

**Process**:
1. Check if image is not None
2. Check if image has valid dimensions (height, width > 32)
3. Return True/False

**Code Location**: `main.py:88-89`
```python
if not validate_image(image):
    raise HTTPException(status_code=400, detail="Invalid image or video")
```

---

### 🔍 **STEP 4: Object Detection (YOLOv8)**

**Service**: `DetectionService` in `services/detection.py`

**Function**: `detect_objects()` 

**Process**:
1. Initialize YOLOv8 model (first time: downloads model ~6MB)
2. Run inference on image: `model(image)`
3. Get bounding boxes for detected objects
4. Filter for:
   - **Person** (class ID: 0)
   - **Cycle/Scooter** (class IDs: 1, 2, 3 - bicycle, car, motorcycle)
5. Return person and cycle bounding boxes

**Code Location**: `main.py:92`
```python
detections = detection_service.detect_objects(image)
```

**Function Details**:
```python
# services/detection.py:18-67
def detect_objects(self, image):
    results = self.model(image, verbose=False)  # YOLOv8 inference
    # Process results
    for box in boxes:
        cls = int(box.cls[0])  # Class ID
        conf = float(box.conf[0])  # Confidence
        xyxy = box.xyxy[0].cpu().numpy().tolist()  # Bounding box
        # Filter for person and cycle
    return {'person': person_box, 'cycle': cycle_box}
```

**Technologies**:
- **YOLOv8 (Ultralytics)**: State-of-the-art object detection
- **PyTorch**: Model inference
- **NumPy**: Array operations

**Model**: `yolov8n.pt` (nano version, fast and accurate)

---

### 👤 **STEP 5: Person Crop**

**Function**: `detect_and_crop_person()` in `services/detection.py`

**Process**:
1. Use person bounding box from Step 4
2. Extract coordinates: [x1, y1, x2, y2]
3. Ensure coordinates are within image bounds
4. Crop person region from image
5. Return cropped person image and bounding box

**Code Location**: `main.py:101`
```python
person_crop, person_bbox = detection_service.detect_and_crop_person(image)
```

**Function Details**:
```python
# services/detection.py:69-95
def detect_and_crop_person(self, image):
    bbox = detections['person']  # Get bounding box
    x1, y1, x2, y2 = map(int, bbox)  # Extract coordinates
    # Ensure bounds
    person_crop = image[y1:y2, x1:x2]  # Crop person
    return person_crop, bbox
```

**Output**: Cropped person image (NumPy array), e.g., 254x592 pixels

---

### 🧬 **STEP 6: Person Embedding Extraction**

**Service**: `ReIDService` in `services/reid.py`

**Function**: `extract_embedding()`

**Process** (Two Methods):

#### Method A: Torchreid (If Available) - **BEST**
1. Load pre-trained person re-ID model (e.g., `osnet_x1_0`)
2. Preprocess image:
   - Convert BGR to RGB
   - Resize to 256x128 (standard person re-ID size)
   - Normalize with ImageNet stats
   - Convert to PyTorch tensor
3. Run model inference
4. Extract feature vector (embedding)
5. Normalize embedding (L2 normalization)

#### Method B: Fallback (If Torchreid Not Available) - **CURRENT**
1. Resize person image to 128x256
2. Convert to multiple color spaces (RGB, HSV, LAB)
3. Compute color histograms (32 bins each channel)
4. Compute texture features (gradient magnitude using Sobel)
5. Combine all features into single vector
6. Normalize embedding

**Code Location**: `main.py:110`
```python
person_embedding = reid_service.extract_embedding(person_crop)
```

**Function Details**:
```python
# services/reid.py:46-97
def extract_embedding(self, person_image):
    if self.model is None:
        return self._simple_feature_extraction(person_image)  # Fallback
    
    # Torchreid method
    rgb_image = cv2.cvtColor(person_image, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb_image, (256, 128))
    # ... preprocessing ...
    features = self.model(image_tensor)  # Model inference
    embedding = features.cpu().numpy()[0]
    embedding = embedding / np.linalg.norm(embedding)  # Normalize
    return embedding
```

**Technologies**:
- **Torchreid**: Deep learning person re-ID (if installed)
- **PyTorch**: Model inference
- **OpenCV**: Image preprocessing
- **NumPy**: Feature computation

**Output**: Embedding vector (e.g., 512-2048 dimensions)

---

### 💾 **STEP 7: Database Storage (Drop-off Only)**

**Service**: `DatabaseService` in `services/database.py`

**Function**: `create_event()`

**Process**:
1. Generate unique event ID (UUID)
2. Prepare event data:
   - Event type: "dropoff" or "pickup"
   - Timestamp: Current UTC time
   - Person embedding: JSON array
   - Person bounding box: JSON array
   - Cycle bounding box: JSON array (if detected)
   - Image path: File path
3. Insert into Supabase database table `events`
4. Return event ID

**Code Location**: `main.py:121`
```python
event_id = db_service.create_event(event_data)
```

**Function Details**:
```python
# services/database.py:33-58
def create_event(self, event):
    event_id = str(uuid.uuid4())  # Generate UUID
    event_data = {
        "event_id": event_id,
        "event_type": event["event_type"],
        "timestamp": datetime.utcnow().isoformat(),
        "person_embedding": json.dumps(event["person_embedding"]),
        # ... more fields ...
    }
    result = self.supabase.table("events").insert(event_data).execute()
    return event_id
```

**Technologies**:
- **Supabase**: PostgreSQL database (cloud)
- **UUID**: Unique identifier generation
- **JSON**: Data serialization

**Database**: PostgreSQL (Supabase)
**Table**: `events`
**Fields**: event_id, event_type, timestamp, person_embedding, person_bbox, cycle_bbox, image_path, match_result, alert_sent

---

### 🔎 **STEP 8: Similarity Comparison (Pickup Only)**

**Service**: `ReIDService` in `services/reid.py`

**Function**: `compute_similarity()`

**Process**:
1. Query database for recent dropoff events (last 10)
2. For each dropoff event:
   - Get stored person embedding
   - Compute cosine similarity with pickup embedding
   - Track best match (highest similarity)
3. Compare best similarity with threshold (default: 0.7)
4. Determine if same person

**Code Location**: `main.py:190-211`
```python
dropoff_events = db_service.get_recent_dropoff_events(limit=10)
for dropoff_event in dropoff_events:
    dropoff_embedding = np.array(dropoff_event['person_embedding'])
    similarity = reid_service.compute_similarity(pickup_embedding, dropoff_embedding)
    if similarity > best_similarity:
        best_similarity = similarity
        best_match_event_id = dropoff_event['event_id']
```

**Function Details**:
```python
# services/reid.py:136-153
def compute_similarity(self, embedding1, embedding2):
    # Normalize embeddings
    emb1 = embedding1 / np.linalg.norm(embedding1)
    emb2 = embedding2 / np.linalg.norm(embedding2)
    # Cosine similarity
    similarity = np.dot(emb1, emb2)
    # Normalize to [0, 1] range
    similarity = (similarity + 1) / 2
    return similarity
```

**Technologies**:
- **NumPy**: Vector operations, dot product
- **Cosine Similarity**: Mathematical similarity measure

**Similarity Score**:
- **0.0 - 0.6**: Different person (low similarity)
- **0.6 - 0.8**: Ambiguous (medium confidence)
- **0.8 - 1.0**: Same person (high confidence)

**Threshold**: 0.7 (configurable in `.env`)

---

### 🤖 **STEP 9: Reka AI Verification (Optional, Pickup Only)**

**Service**: `RekaAIService` in `services/reka_ai.py`

**Function**: `analyze_person_similarity()`

**Process** (Only if):
1. Reka AI is configured (API key in `.env`)
2. Similarity is ambiguous (0.6 - 0.75)
3. Confidence is "medium"

**Steps**:
1. Load dropoff image from database
2. Extract person crop from dropoff image
3. Convert both person crops to JPEG bytes
4. Send to Reka AI API with prompt
5. Parse response (yes/no + confidence)
6. Override result if Reka AI confidence > 0.7

**Code Location**: `main.py:227-257`
```python
if reka_service.is_configured() and (confidence == "medium" or (0.6 <= best_similarity < 0.75)):
    reka_result = reka_service.analyze_person_similarity(
        dropoff_buffer.tobytes(),
        pickup_buffer.tobytes()
    )
    if reka_result and reka_result['confidence'] > 0.7:
        is_same_person = reka_result['is_same_person']
        confidence = "high"
```

**Technologies**:
- **Reka AI API**: Advanced vision analysis
- **HTTP Requests**: API calls
- **Base64 Encoding**: Image encoding

**API Endpoint**: `https://api.reka.ai/v1/chat`
**Method**: POST
**Payload**: JSON with images (base64) and prompt

---

### 🚨 **STEP 10: Alert System (Pickup Only)**

**Service**: `AlertService` in `services/alert.py`

**Function**: `send_security_alert()`

**Process** (Only if different person detected):
1. Check if Telegram is configured
2. Prepare alert message:
   - Event ID
   - Similarity score
   - Warning message
3. Send alert via Telegram Bot API
4. Optionally send SMS via Twilio

**Code Location**: `main.py:279-285`
```python
if not match_result.is_same_person:
    alert_sent = alert_service.send_security_alert(
        event_id=event_id,
        similarity_score=match_result.similarity_score,
        image_path=file_path
    )
```

**Function Details**:
```python
# services/alert.py:58-78
def send_security_alert(self, event_id, similarity_score, image_path):
    message = f"🚨 SECURITY ALERT - CycleGuard AI\n\n"
    message += f"⚠️ Unauthorized pickup detected!\n"
    message += f"Event ID: {event_id}\n"
    message += f"Similarity Score: {similarity_score:.2f}\n"
    # Send via Telegram
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        files={'photo': open(image_path, 'rb')},
        data={'chat_id': chat_id, 'caption': message}
    )
    return response.status_code == 200
```

**Technologies**:
- **Telegram Bot API**: Instant messaging
- **Twilio**: SMS (optional)
- **HTTP Requests**: API calls

**API Endpoints**:
- Telegram: `https://api.telegram.org/bot{token}/sendPhoto`
- Twilio: `https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json`

---

### 📊 **STEP 11: Database Update (Pickup Only)**

**Function**: `update_event_match_result()` in `services/database.py`

**Process**:
1. Prepare match result data:
   - `is_same_person`: Boolean
   - `similarity_score`: Float
   - `confidence`: String ("high", "medium", "low")
   - `matched_event_id`: UUID of matched dropoff event
   - `alert_sent`: Boolean
2. Update event in database
3. Store match result as JSON

**Code Location**: `main.py:287`
```python
db_service.update_event_match_result(event_id, match_result, alert_sent)
```

---

### 📤 **STEP 12: Response Generation**

**Function**: `JSONResponse` in FastAPI

**Process**:
1. Prepare response JSON:
   - Event ID
   - Status: "success"
   - Match result (pickup only)
   - Alert sent status (pickup only)
   - Detections (person, cycle)
2. Return HTTP 200 response

**Code Location**: `main.py:289-307`
```python
return JSONResponse(
    status_code=200,
    content={
        "event_id": event_id,
        "status": "success",
        "match_result": {...},
        "alert_sent": alert_sent,
        "detections": {...}
    }
)
```

---

## APIs and Functions Used

### Main API Endpoints

1. **POST /api/dropoff**
   - Function: `register_dropoff()`
   - Input: Video/image file
   - Output: Event ID, detections

2. **POST /api/pickup**
   - Function: `register_pickup()`
   - Input: Video/image file
   - Output: Event ID, match result, alert status

3. **GET /api/events**
   - Function: `get_events()`
   - Output: List of events

4. **GET /api/events/{event_id}**
   - Function: `get_event()`
   - Output: Event details

### Service Functions

#### DetectionService
- `detect_objects(image)`: Detect person and cycle
- `detect_and_crop_person(image)`: Crop person from image

#### ReIDService
- `extract_embedding(person_image)`: Extract person embedding
- `compute_similarity(emb1, emb2)`: Compute cosine similarity
- `_simple_feature_extraction(image)`: Fallback feature extraction

#### DatabaseService
- `create_event(event_data)`: Create event in database
- `get_recent_dropoff_events(limit)`: Get recent dropoffs
- `update_event_match_result(event_id, match_result, alert_sent)`: Update event
- `get_event(event_id)`: Get event by ID
- `get_all_events(limit, offset)`: Get all events

#### AlertService
- `send_telegram_alert(message, image_path)`: Send Telegram alert
- `send_sms_alert(message, phone_number)`: Send SMS alert
- `send_security_alert(event_id, similarity_score, image_path)`: Send security alert

#### RekaAIService
- `analyze_person_similarity(img1_bytes, img2_bytes)`: Analyze with Reka AI
- `is_configured()`: Check if Reka AI is configured

### Utility Functions

#### Image Processing
- `save_uploaded_file(file, upload_dir)`: Save uploaded file
- `extract_frame_from_video(video_path, frame_index)`: Extract video frame
- `validate_image(image)`: Validate image
- `load_image(image_path)`: Load image from file
- `crop_bbox(image, bbox)`: Crop image using bounding box
- `resize_image(image, size)`: Resize image

---

## Data Flow Diagram

```
┌─────────────────┐
│  Video Upload   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save to Disk   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Frame   │ (OpenCV)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  YOLOv8 Detect  │ (Person + Cycle)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Crop Person    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Embedding│ (Torchreid or Fallback)
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌──────────────┐    ┌──────────────┐
│  Drop-off    │    │   Pickup     │
│  Event       │    │   Event      │
└──────┬───────┘    └──────┬───────┘
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│  Store in    │    │  Query DB    │
│  Database    │    │  for Dropoffs│
└──────────────┘    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Compare     │
                    │  Embeddings  │
                    └──────┬───────┘
                           │
                           ├─ Similarity > 0.7 → Same Person
                           │
                           ├─ Similarity 0.6-0.7 → Reka AI (if configured)
                           │
                           └─ Similarity < 0.7 → Different Person → Alert
```

---

## Summary

### Technologies at Each Step

1. **Upload**: FastAPI, aiofiles
2. **Frame Extraction**: OpenCV
3. **Detection**: YOLOv8 (Ultralytics), PyTorch
4. **Person Crop**: NumPy, OpenCV
5. **Embedding**: Torchreid (or fallback), PyTorch, OpenCV, NumPy
6. **Database**: Supabase (PostgreSQL)
7. **Similarity**: NumPy (cosine similarity)
8. **Reka AI**: HTTP requests, Reka AI API
9. **Alerts**: Telegram Bot API, Twilio
10. **Response**: FastAPI, JSON

### Key Metrics

- **Video Processing**: ~2-5 seconds per video
- **Object Detection**: ~0.5-1 second
- **Embedding Extraction**: ~0.5-2 seconds
- **Similarity Comparison**: <0.1 seconds
- **Database Query**: ~0.1-0.5 seconds
- **Total Processing**: ~3-8 seconds per video

### Current Status

- ✅ **Working**: YOLOv8 detection, fallback embedding extraction
- ⚠️ **Needs Improvement**: Install torchreid for better accuracy
- ⚠️ **Optional**: Reka AI (not configured), Supabase (not configured)

---

This completes the comprehensive workflow documentation. The system processes videos through detection, embedding extraction, similarity comparison, and alerting to provide cycle security monitoring.

