from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Twilio
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Reka AI (Optional)
    reka_api_key: Optional[str] = None
    
    # Similarity threshold for person matching (0.85 recommended for torchreid)
    similarity_threshold: float = 0.85
    
    # Model paths
    yolo_model_path: str = "yolov8n.pt"
    reid_model_name: str = "osnet_x1_0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

