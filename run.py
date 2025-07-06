#!/usr/bin/env python3
"""
Main runner script untuk Twitter Hoax Detector Application
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def run_web_server():
    """Run web server dengan konfigurasi yang benar"""
    try:
        import uvicorn
        
        # Menggunakan import string untuk mendukung reload
        uvicorn.run(
            "app.main:app",  # Import string format
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error running web server: {e}")
        sys.exit(1)

def run_telegram_bot():
    """Run Telegram bot"""
    try:
        from telegram_bot import main as telegram_main
        
        print("🤖 Starting Telegram Bot...")
        asyncio.run(telegram_main())
    except Exception as e:
        print(f"Error running telegram bot: {e}")
        sys.exit(1)

def run_both():
    """Run both web server and telegram bot"""
    import threading
    import time
    
    # Run telegram bot in separate thread
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    
    # Give telegram bot time to start
    time.sleep(2)
    
    # Run web server (this will block)
    run_web_server()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Twitter Hoax Detector")
    parser.add_argument(
        "--mode", 
        choices=["web", "telegram", "both"], 
        default="web",
        help="Mode to run the application"
    )
    
    args = parser.parse_args()
    
    # Initialize database
    print("🔄 Initializing database...")
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Run based on mode
    if args.mode == "web":
        print("🌐 Starting Web Server...")
        run_web_server()
    elif args.mode == "telegram":
        run_telegram_bot()
    elif args.mode == "both":
        print("🚀 Starting both Web Server and Telegram Bot...")
        run_both()

if __name__ == "__main__":
    main() 