# Testing Guide for CycleGuard AI

## Video Testing Setup

### 1. Prepare Test Videos

Upload three videos to the `test_videos/` folder:

1. **dropoff_video.mp4** - Person dropping off/parking a scooter
2. **pickup_same_person.mp4** - Same person picking up the scooter
3. **pickup_different_person.mp4** - Different person picking up the scooter

### 2. Video Requirements

- **Format**: .mp4, .mov, .avi, .mkv (any format supported by OpenCV)
- **Quality**: Good lighting, person clearly visible
- **Duration**: 5-30 seconds recommended
- **Content**: 
  - Person should be visible throughout the video
  - Scooter/cycle should be visible
  - Clear view of person's clothing and appearance

### 3. Running Tests

#### Option 1: Automated Test Script

```bash
# Make sure the API server is running
uvicorn main:app --reload

# In another terminal, run the test script
python test_video_flow.py
```

The script will:
1. Check if API is running
2. Test dropoff event
3. Test pickup with same person
4. Test pickup with different person
5. Show event history

#### Option 2: Manual Testing with curl

```bash
# 1. Dropoff
curl -X POST "http://localhost:8000/api/dropoff" \
  -F "file=@test_videos/dropoff_video.mp4"

# 2. Pickup (same person)
curl -X POST "http://localhost:8000/api/pickup" \
  -F "file=@test_videos/pickup_same_person.mp4"

# 3. Pickup (different person)
curl -X POST "http://localhost:8000/api/pickup" \
  -F "file=@test_videos/pickup_different_person.mp4"
```

#### Option 3: Using Python

```python
import requests

# Dropoff
with open('test_videos/dropoff_video.mp4', 'rb') as f:
    files = {'file': ('dropoff_video.mp4', f, 'video/mp4')}
    response = requests.post('http://localhost:8000/api/dropoff', files=files)
    print(response.json())

# Pickup (same person)
with open('test_videos/pickup_same_person.mp4', 'rb') as f:
    files = {'file': ('pickup_same_person.mp4', f, 'video/mp4')}
    response = requests.post('http://localhost:8000/api/pickup', files=files)
    print(response.json())

# Pickup (different person)
with open('test_videos/pickup_different_person.mp4', 'rb') as f:
    files = {'file': ('pickup_different_person.mp4', f, 'video/mp4')}
    response = requests.post('http://localhost:8000/api/pickup', files=files)
    print(response.json())
```

## Expected Results

### Dropoff Event
- **Status**: Success
- **Person detected**: True
- **Cycle detected**: True (if visible)
- **Event ID**: Generated UUID

### Pickup Event (Same Person)
- **Status**: Success
- **is_same_person**: True
- **Similarity score**: High (0.7+)
- **Confidence**: High or Medium
- **Alert sent**: False

### Pickup Event (Different Person)
- **Status**: Success
- **is_same_person**: False
- **Similarity score**: Low (<0.7)
- **Confidence**: Low or Medium
- **Alert sent**: True (if Telegram/Twilio configured)

## Troubleshooting

### Issue: "No person detected"
**Solutions:**
- Ensure person is clearly visible in the video
- Check lighting conditions
- Try a different frame (system uses middle frame)
- Verify video format is supported

### Issue: "Could not extract frame from video"
**Solutions:**
- Check video file is not corrupted
- Try converting video to .mp4 format
- Verify OpenCV can read the video file

### Issue: Low similarity scores
**Solutions:**
- Ensure same lighting conditions
- Same person should wear similar clothing
- Check person is facing camera in both videos
- Adjust `SIMILARITY_THRESHOLD` in .env if needed

### Issue: False positives/negatives
**Solutions:**
- Adjust `SIMILARITY_THRESHOLD` in .env
- Ensure good quality videos
- Verify person is clearly visible
- Consider using Reka AI for ambiguous cases (when configured)

## Testing Without Reka AI

The system works perfectly without Reka AI:
- Uses torchreid for person matching
- Falls back to simple feature extraction if torchreid unavailable
- Reka AI is only used for ambiguous cases (medium confidence)
- System will show: "ℹ️  Reka AI is not configured. Continuing without Reka AI"

## Performance Testing

### Video Processing Time
- Small video (<10MB): ~2-5 seconds
- Medium video (10-50MB): ~5-15 seconds
- Large video (>50MB): ~15-30 seconds

### Factors Affecting Performance
- Video file size
- Video resolution
- YOLOv8 model loading (first request)
- Torchreid model loading (first request)
- Database connection speed

## Monitoring

### Check API Health
```bash
curl http://localhost:8000/api/health
```

### View Events
```bash
curl http://localhost:8000/api/events?limit=10
```

### View Specific Event
```bash
curl http://localhost:8000/api/events/{event_id}
```

## Next Steps

1. **Test with real videos**: Use actual dropoff/pickup scenarios
2. **Adjust thresholds**: Fine-tune `SIMILARITY_THRESHOLD` based on results
3. **Monitor alerts**: Verify Telegram/Twilio alerts are working
4. **Check database**: Verify events are stored correctly in Supabase
5. **Performance tuning**: Optimize for your use case

