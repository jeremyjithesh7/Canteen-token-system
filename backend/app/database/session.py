from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.config import settings
from typing import Generator
import os

# Normalize database URL for SQLAlchemy compatibility
db_url = settings.DATABASE_URL or os.getenv("DATABASE_URL", "sqlite:///./canteen.db")

# Neon and other PostgreSQL cloud providers often supply 'postgres://' which SQLAlchemy requires as 'postgresql://'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine_kwargs = {
    "pool_pre_ping": True
}

if db_url.startswith("sqlite"):
    # SQLite local dev options
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL / Neon Serverless configuration
    # Connection pooling tuned for serverless functions
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(
    db_url,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
