# CycleGuard AI API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running and services are ready.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "services": {
    "detection": "ready",
    "reid": "ready",
    "database": "ready",
    "alert": "ready"
  }
}
```

### 2. Register Drop-off Event
**POST** `/api/dropoff`

Register a drop-off event when someone parks a cycle/escooter.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image or video file)

**Response:**
```json
{
  "event_id": "uuid",
  "status": "success",
  "person_embedding_id": "uuid",
  "message": "Drop-off event recorded successfully",
  "detections": {
    "person_detected": true,
    "cycle_detected": true
  }
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/dropoff" \
  -F "file=@person_parking.jpg"
```

**Example using Python:**
```python
import requests

with open('person_parking.jpg', 'rb') as f:
    files = {'file': ('person_parking.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/api/dropoff', files=files)
    print(response.json())
```

### 3. Register Pickup Event
**POST** `/api/pickup`

Register a pickup event when someone attempts to pick up a cycle/escooter.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image or video file)

**Response:**
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

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/pickup" \
  -F "file=@person_picking_up.jpg"
```

### 4. Get All Events
**GET** `/api/events`

Get all events with pagination.

**Query Parameters:**
- `limit` (optional): Number of events to return (default: 100)
- `offset` (optional): Number of events to skip (default: 0)

**Response:**
```json
{
  "events": [
    {
      "event_id": "uuid",
      "event_type": "dropoff",
      "timestamp": "2024-01-01T00:00:00",
      "person_bbox": [100, 200, 300, 400],
      "cycle_bbox": [50, 150, 250, 350],
      "match_result": null,
      "alert_sent": false
    }
  ],
  "count": 1,
  "limit": 100,
  "offset": 0
}
```

### 5. Get Event by ID
**GET** `/api/events/{event_id}`

Get a specific event by its ID.

**Response:**
```json
{
  "event_id": "uuid",
  "event_type": "pickup",
  "timestamp": "2024-01-01T00:00:00",
  "person_embedding": [0.1, 0.2, ...],
  "person_bbox": [100, 200, 300, 400],
  "cycle_bbox": [50, 150, 250, 350],
  "image_path": "uploads/image.jpg",
  "match_result": {
    "is_same_person": false,
    "similarity_score": 0.45,
    "confidence": "low",
    "matched_event_id": "uuid"
  },
  "alert_sent": true
}
```

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "detail": "No person detected in image. Please ensure a person is visible."
}
```

**404 Not Found:**
```json
{
  "detail": "Event not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error processing dropoff: ..."
}
```

## Testing

Use the provided test client:
```bash
python test_client.py <dropoff_image_path> [pickup_image_path]
```

Example:
```bash
python test_client.py person1.jpg person2.jpg
```

## Integration Examples

### Python
```python
import requests

# Drop-off event
with open('dropoff.jpg', 'rb') as f:
    files = {'file': ('dropoff.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/api/dropoff', files=files)
    dropoff_event = response.json()
    print(f"Drop-off event ID: {dropoff_event['event_id']}")

# Pickup event
with open('pickup.jpg', 'rb') as f:
    files = {'file': ('pickup.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/api/pickup', files=files)
    pickup_event = response.json()
    print(f"Match result: {pickup_event['match_result']}")
    print(f"Alert sent: {pickup_event['alert_sent']}")
```

### JavaScript/Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

// Drop-off event
const formData = new FormData();
formData.append('file', fs.createReadStream('dropoff.jpg'));

axios.post('http://localhost:8000/api/dropoff', formData, {
  headers: formData.getHeaders()
})
.then(response => {
  console.log('Drop-off event:', response.data);
})
.catch(error => {
  console.error('Error:', error.response.data);
});
```

### cURL
```bash
# Drop-off
curl -X POST "http://localhost:8000/api/dropoff" \
  -F "file=@dropoff.jpg"

# Pickup
curl -X POST "http://localhost:8000/api/pickup" \
  -F "file=@pickup.jpg"

# Get events
curl "http://localhost:8000/api/events?limit=10"

# Get event by ID
curl "http://localhost:8000/api/events/{event_id}"
```

