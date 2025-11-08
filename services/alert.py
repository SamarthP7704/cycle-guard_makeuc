from typing import Optional
from config import settings
import requests

# Try to import Twilio, but continue without it if not available
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    TwilioClient = None


class AlertService:
    """Service for sending alerts via Telegram and Twilio"""
    
    def __init__(self):
        self.telegram_token = settings.telegram_bot_token
        self.telegram_chat_id = settings.telegram_chat_id
        self.twilio_client = None
        
        if TWILIO_AVAILABLE and settings.twilio_account_sid and settings.twilio_auth_token:
            try:
                self.twilio_client = TwilioClient(
                    settings.twilio_account_sid,
                    settings.twilio_auth_token
                )
            except Exception as e:
                print(f"Error initializing Twilio client: {e}")
                self.twilio_client = None
        else:
            self.twilio_client = None
    
    def send_telegram_alert(self, message: str, image_path: Optional[str] = None) -> bool:
        """Send alert via Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            print("Telegram credentials not configured")
            return False
        
        try:
            base_url = f"https://api.telegram.org/bot{self.telegram_token}"
            
            if image_path:
                # Send photo with caption
                with open(image_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {
                        'chat_id': self.telegram_chat_id,
                        'caption': message
                    }
                    response = requests.post(
                        f"{base_url}/sendPhoto",
                        files=files,
                        data=data,
                        timeout=10
                    )
            else:
                # Send text message
                response = requests.post(
                    f"{base_url}/sendMessage",
                    json={
                        'chat_id': self.telegram_chat_id,
                        'text': message
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                print(f"Telegram alert sent successfully")
                return True
            else:
                print(f"Failed to send Telegram alert: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
            return False
    
    def send_sms_alert(self, message: str, phone_number: str) -> bool:
        """Send SMS alert via Twilio"""
        if not self.twilio_client or not settings.twilio_phone_number:
            print("Twilio credentials not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.twilio_phone_number,
                to=phone_number
            )
            print(f"SMS alert sent successfully: {message.sid}")
            return True
        except Exception as e:
            print(f"Error sending SMS alert: {e}")
            return False
    
    def send_security_alert(self, event_id: str, similarity_score: float, image_path: Optional[str] = None) -> bool:
        """Send security alert for unauthorized pickup attempt"""
        message = f"🚨 SECURITY ALERT - CycleGuard AI\n\n"
        message += f"⚠️ Unauthorized pickup detected!\n"
        message += f"Event ID: {event_id}\n"
        message += f"Similarity Score: {similarity_score:.2f}\n"
        message += f"A different person is attempting to pick up a cycle/escooter.\n"
        message += f"Please verify immediately."
        
        # Try Telegram first, then SMS
        telegram_sent = self.send_telegram_alert(message, image_path)
        
        # You can also send SMS if phone number is provided
        # sms_sent = self.send_sms_alert(message, "+1234567890")
        
        return telegram_sent

