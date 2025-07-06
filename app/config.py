import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Twitter API
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    
    # Brave Search API
    BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hoax_detector.db")
    
    # App Settings
    APP_NAME = os.getenv("APP_NAME", "Twitter Hoax Detector")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Analysis Settings
    HOAX_THRESHOLD = float(os.getenv("HOAX_THRESHOLD", "0.7"))  # Threshold untuk menentukan hoax
    BOT_DETECTION_THRESHOLD = float(os.getenv("BOT_DETECTION_THRESHOLD", "0.6"))  # Threshold untuk menentukan bot
    
    # File paths
    REPORTS_DIR = "reports"
    VISUALIZATIONS_DIR = "visualizations"
    STATIC_DIR = "static"
    TEMPLATES_DIR = "templates"

config = Config() 