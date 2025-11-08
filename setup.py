"""
Setup script for CycleGuard AI
"""
import os
import subprocess
import sys


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✓ Created .env file from .env.example")
            print("  Please update .env with your credentials")
        else:
            print("⚠ .env.example not found, creating basic .env file")
            with open('.env', 'w') as f:
                f.write("""SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone
REKA_API_KEY=your_reka_api_key
SIMILARITY_THRESHOLD=0.7
""")
    else:
        print("✓ .env file already exists")


def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'database']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("⚠ Error installing dependencies. Please install manually:")
        print("  pip install -r requirements.txt")
        return False
    return True


def download_yolo_model():
    """Download YOLOv8 model if not present"""
    print("\nChecking YOLOv8 model...")
    model_path = "yolov8n.pt"
    if not os.path.exists(model_path):
        print("YOLOv8 model will be downloaded on first run")
    else:
        print(f"✓ YOLOv8 model found: {model_path}")


def main():
    """Main setup function"""
    print("=" * 50)
    print("CycleGuard AI Setup")
    print("=" * 50)
    print()
    
    check_python_version()
    create_env_file()
    create_directories()
    download_yolo_model()
    
    print("\n" + "=" * 50)
    print("Setup Steps:")
    print("=" * 50)
    print("1. Update .env file with your credentials:")
    print("   - Supabase URL and key")
    print("   - Telegram bot token and chat ID (optional)")
    print("   - Twilio credentials (optional)")
    print("   - Reka API key (optional)")
    print()
    print("2. Set up Supabase database:")
    print("   - Create a new Supabase project")
    print("   - Run the SQL script in database/schema.sql")
    print()
    print("3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("4. Run the application:")
    print("   uvicorn main:app --reload")
    print("   or")
    print("   python main.py")
    print()
    print("=" * 50)
    
    # Ask if user wants to install dependencies
    response = input("\nDo you want to install dependencies now? (y/n): ")
    if response.lower() == 'y':
        install_dependencies()
    else:
        print("Skipping dependency installation. Please run: pip install -r requirements.txt")


if __name__ == "__main__":
    main()

