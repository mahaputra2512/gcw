from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import config
import os

# Buat direktori untuk database jika belum ada
os.makedirs(os.path.dirname(config.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)

# Buat engine SQLAlchemy
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Untuk SQLite
)

# Buat session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Buat semua tabel dalam database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency untuk mendapatkan session database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inisialisasi database dengan data awal jika diperlukan"""
    create_tables()
    print("Database initialized successfully!") 