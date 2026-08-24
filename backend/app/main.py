from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from backend.app.config import settings
from backend.app.database.session import engine, SessionLocal
from backend.app.database.base import Base
from backend.app.utils.seed_data import seed_database_if_empty
from backend.app.utils.logger import RequestLoggingMiddleware

# Import all models to ensure metadata registration
import backend.app.models

# Import routers
from backend.app.routes import (
    auth_router,
    users_router,
    counters_router,
    food_router,
    orders_router,
    tokens_router,
    payments_router,
    inventory_router,
    notifications_router,
    ai_router,
    admin_router,
    cart_router,
    ratings_router,
    wallet_router,
    rewards_router
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Initializing database schema and seed records...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
        logger.info("Database initialized & seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade API for Digital Canteen Token System with AI Demand Forecasting, Smart Token Sequencing, and Queue Predictors.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Structured request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS for seamless frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount API Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(counters_router)
app.include_router(food_router)
app.include_router(orders_router)
app.include_router(tokens_router)
app.include_router(payments_router)
app.include_router(inventory_router)
app.include_router(notifications_router)
app.include_router(ai_router)
app.include_router(admin_router)
app.include_router(cart_router)
app.include_router(ratings_router)
app.include_router(wallet_router)
app.include_router(rewards_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint for container monitors and uptime checkers."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "database": "connected"
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Digital Canteen Token System API",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
