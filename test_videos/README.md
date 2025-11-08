# Test Videos Folder

Upload your test videos here for testing CycleGuard AI.

## Required Videos

1. **dropoff_video.mp4** (or .mov, .avi)
   - Video of a person dropping off/parking a scooter
   - This will be used to register the drop-off event

2. **pickup_same_person.mp4** (or .mov, .avi)
   - Video of the SAME person picking up the scooter
   - This should match the person from dropoff_video.mp4
   - System should detect: `is_same_person: true`

3. **pickup_different_person.mp4** (or .mov, .avi)
   - Video of a DIFFERENT person picking up the scooter
   - This should be a different person than dropoff_video.mp4
   - System should detect: `is_same_person: false` and send an alert

## Video Requirements

- Supported formats: .mp4, .mov, .avi, .mkv
- Person should be clearly visible in the video
- Scooter/cycle should be visible
- Good lighting conditions for better detection
- Video length: 5-30 seconds recommended

## Usage

After uploading videos, use the test script:
```bash
python test_video_flow.py
```

Or test manually using the API:
```bash
# Dropoff
curl -X POST "http://localhost:8000/api/dropoff" \
  -F "file=@test_videos/dropoff_video.mp4"

# Pickup (same person)
curl -X POST "http://localhost:8000/api/pickup" \
  -F "file=@test_videos/pickup_same_person.mp4"

# Pickup (different person)
curl -X POST "http://localhost:8000/api/pickup" \
  -F "file=@test_videos/pickup_different_person.mp4"
```

