import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Digital Canteen Token System"
    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
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
    
    # Demo Payment
    DEMO_PAYMENT_ENABLED: bool = True
    DEMO_PAYMENT_GATEWAY_NAME: str = "DemoPay Gateway"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
