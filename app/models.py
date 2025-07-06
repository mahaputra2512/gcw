from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class TwitterUser(Base):
    """Model untuk data pengguna Twitter"""
    __tablename__ = "twitter_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)  # Twitter user ID
    username = Column(String, index=True)
    display_name = Column(String)
    bio = Column(Text)
    followers_count = Column(Integer)
    following_count = Column(Integer)
    tweet_count = Column(Integer)
    account_creation_date = Column(DateTime)
    verified = Column(Boolean, default=False)
    profile_image_url = Column(String)
    
    # Bot detection metrics
    bot_probability = Column(Float, default=0.0)
    is_bot = Column(Boolean, default=False)
    bot_detection_date = Column(DateTime)
    
    # Relationship dengan tweets
    tweets = relationship("Tweet", back_populates="user")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Tweet(Base):
    """Model untuk data tweet"""
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, index=True)  # Twitter tweet ID
    url = Column(String)
    text = Column(Text)
    created_at_twitter = Column(DateTime)
    
    # Metrics Twitter
    retweet_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    
    # User yang memposting
    user_id = Column(String, ForeignKey("twitter_users.user_id"))
    user = relationship("TwitterUser", back_populates="tweets")
    
    # Hasil analisis
    analyses = relationship("HoaxAnalysis", back_populates="tweet")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HoaxAnalysis(Base):
    """Model untuk hasil analisis hoax"""
    __tablename__ = "hoax_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id"))
    
    # Hasil analisis OpenAI
    openai_analysis = Column(Text)
    hoax_probability = Column(Float)
    is_hoax = Column(Boolean)
    hoax_reasons = Column(JSON)  # List alasan mengapa dianggap hoax
    
    # Hasil fact-checking dari Brave Search
    fact_check_results = Column(JSON)
    supporting_sources = Column(JSON)  # Sumber yang mendukung
    contradicting_sources = Column(JSON)  # Sumber yang bertentangan
    
    # Network analysis
    network_data = Column(JSON)  # Data graf jaringan
    influence_score = Column(Float)  # Skor pengaruh penyebaran
    
    # File paths untuk visualisasi dan laporan
    network_visualization_path = Column(String)
    influence_chart_path = Column(String)
    pdf_report_path = Column(String)
    
    # Relationship
    tweet = relationship("Tweet", back_populates="analyses")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalysisSession(Base):
    """Model untuk session analisis (untuk tracking request dari user)"""
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    
    # Input dari user
    tweet_url = Column(String)
    user_ip = Column(String)
    user_agent = Column(String)
    
    # Status analisis
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text)
    
    # Hasil
    analysis_id = Column(Integer, ForeignKey("hoax_analyses.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TelegramUser(Base):
    """Model untuk pengguna Telegram bot"""
    __tablename__ = "telegram_users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    
    # Statistics
    total_requests = Column(Integer, default=0)
    last_request_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 