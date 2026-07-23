from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # 🟢 Tests connection before running queries; automatically reconnects dropped SSL links
    pool_recycle=280,         # 🟢 Recycles connections before Render's 300s timeout
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    connect_args={
        "keepalives": 1,      # 🟢 Sends TCP keepalive signals to prevent connection drops on heavy jobs
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()