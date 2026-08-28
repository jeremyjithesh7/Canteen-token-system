import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Digital Canteen Token System"
    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS Configuration: Comma-separated list of allowed origins
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:5173,http://127.0.0.1:5173"
    
    # Database
    DATABASE_URL: str = "sqlite:///./canteen.db"
    
    # JWT
    SECRET_KEY: str = "canteen-super-secure-production-jwt-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # Business Logic
    AVERAGE_PREPARATION_TIME_MINUTES: int = 10
    DEFAULT_DAILY_STOCK_LIMIT: int = 100
    LOW_STOCK_THRESHOLD_ALERT: int = 10
    
    # AI Logic
    AI_MODEL_CONFIDENCE_THRESHOLD: float = 0.75
    CROWD_PEAK_THRESHOLD_QUEUE_DEPTH: int = 8
    
    # Real UPI Payment Configuration
    UPI_VPA: str = "jeremyjithesh7@oksbi"
    UPI_PAYEE_NAME: str = "Jeremy Jithesh"
    UPI_MERCHANT_CODE: str = "5812" # Canteen & Food Services
    CAMPUS_GST_PERCENT: float = 5.0 # 5% Campus GST

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
            ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
