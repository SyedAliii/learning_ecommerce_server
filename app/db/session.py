import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path
from dotenv import load_dotenv
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
print("Base Directory:", BASE_DIR)

# load_dotenv(BASE_DIR / ".env")

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
print("Database URL:", SQLALCHEMY_DATABASE_URL)

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set in .env")

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()