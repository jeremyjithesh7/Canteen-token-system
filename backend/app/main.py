from fastapi import FastAPI, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os

from backend.app.config import settings
from backend.app.database.session import engine, SessionLocal, get_db
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
    rewards_router,
    database_viewer_router
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Initializing database schema and seed records...")
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_database_if_empty(db)
            logger.info("Database initialized & seeded successfully.")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database connection / startup error: {e}")
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

# Configure CORS with explicit, environment-driven origins
raw_origins = getattr(settings, "ALLOWED_ORIGINS", "")
allowed_origins_list = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
if not allowed_origins_list:
    allowed_origins_list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global exception handler - masks stack traces in production (DEBUG=False)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "type": type(exc).__name__}
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact canteen support."}
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
app.include_router(database_viewer_router)

@app.get("/api/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that actively tests database connection and reports environment status."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"

    is_healthy = db_status == "connected"
    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "debug": settings.DEBUG,
        "database": db_status
    }

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
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
