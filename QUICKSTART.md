# CycleGuard AI - Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- Supabase account (free tier works)
- Telegram Bot (optional, for alerts)
- Twilio account (optional, for SMS alerts)

## Step-by-Step Setup

### 1. Clone/Download the Project
```bash
cd cycle_guard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with torchreid, you may need to install it separately:
```bash
pip install torchreid
# Or from source:
# pip install git+https://github.com/KaiyangZhou/deep-person-reid.git
```

### 3. Set Up Supabase Database

1. Go to [Supabase](https://supabase.com) and create a new project
2. Wait for the project to be ready (takes 1-2 minutes)
3. Go to SQL Editor in your Supabase dashboard
4. Copy the contents of `database/schema.sql`
5. Paste and run it in the SQL Editor
6. Verify the `events` table was created

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   TELEGRAM_CHAT_ID=your-telegram-chat-id
   SIMILARITY_THRESHOLD=0.7
   ```

3. To get Supabase credentials:
   - Go to your Supabase project settings
   - Click on "API" in the sidebar
   - Copy "Project URL" (SUPABASE_URL)
   - Copy "anon public" key (SUPABASE_KEY)

### 5. Set Up Telegram Bot (Optional)

1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow instructions
3. Copy the bot token to `.env` as `TELEGRAM_BOT_TOKEN`
4. To get your chat ID:
   - Start a chat with your bot
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response
   - Add it to `.env` as `TELEGRAM_CHAT_ID`

### 6. Run the Application

```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the run script
./run.sh

# Option 3: Run directly
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 7. Test the API

Open your browser and visit:
- http://localhost:8000 - API root
- http://localhost:8000/api/health - Health check
- http://localhost:8000/docs - Interactive API documentation

### 8. Test with Images

```bash
# Using the test client
python test_client.py path/to/dropoff_image.jpg path/to/pickup_image.jpg

# Or using curl
curl -X POST "http://localhost:8000/api/dropoff" \
  -F "file=@path/to/dropoff_image.jpg"
```

## Troubleshooting

### Issue: "No module named 'torchreid'"
**Solution:** Install torchreid manually:
```bash
pip install torchreid
```

### Issue: "Supabase connection error"
**Solution:** 
- Verify your SUPABASE_URL and SUPABASE_KEY are correct
- Make sure you've run the SQL schema in Supabase
- Check that your Supabase project is active

### Issue: "YOLOv8 model download failed"
**Solution:** 
- Check your internet connection
- The model will be downloaded automatically on first run
- Model file is ~6MB

### Issue: "No person detected"
**Solution:**
- Ensure the image contains a clearly visible person
- Try with a different image
- Check that the image is in a supported format (jpg, png, etc.)

### Issue: "Telegram alerts not working"
**Solution:**
- Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are correct
- Make sure you've started a conversation with your bot
- Check that the bot has permission to send messages

## Next Steps

1. **Test with Real Images**: Use images of people with cycles/scooters
2. **Set Up Monitoring**: Monitor the API logs for events
3. **Customize Thresholds**: Adjust `SIMILARITY_THRESHOLD` in `.env`
4. **Integrate with Cameras**: Connect to IP cameras or webcams
5. **Deploy**: Deploy to cloud (Heroku, AWS, etc.)

## API Usage Examples

### Register Dropoff Event
```python
import requests

with open('dropoff.jpg', 'rb') as f:
    files = {'file': ('dropoff.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/api/dropoff', files=files)
    print(response.json())
```

### Register Pickup Event
```python
import requests

with open('pickup.jpg', 'rb') as f:
    files = {'file': ('pickup.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/api/pickup', files=files)
    result = response.json()
    print(f"Same person: {result['match_result']['is_same_person']}")
    print(f"Alert sent: {result['alert_sent']}")
```

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review API_DOCS.md for API reference
3. Check PROJECT_SUMMARY.md for architecture overview

## License

MIT License

