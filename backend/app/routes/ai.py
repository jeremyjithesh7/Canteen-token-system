from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.app.database.session import get_db
from backend.app.schemas.ai import (
    DemandForecastResponse,
    FoodRecommendationItem,
    QueueStatusResponse,
    PredictionOverrideCreate,
    PredictionOverrideResponse,
    DemandVsActualResponse,
    CrowdForecastResponse,
    InventoryIntelligenceResponse
)
from backend.app.schemas.waste import FoodWasteAnalyticsResponse
from backend.app.services.ai_service import AIService
from backend.app.authentication.deps import get_current_active_user, get_current_staff_or_admin, get_current_admin
from backend.app.models.user import User

router = APIRouter(prefix="/api/ai", tags=["AI & Machine Learning"])

@router.get("/recommendations", response_model=List[FoodRecommendationItem])
def get_personalized_recommendations(
    top_n: int = Query(4, ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Returns AI-recommended food items with honest explanation reasons."""
    return AIService.get_food_recommendations(db=db, user_id=current_user.id, top_n=top_n)

@router.get("/crowd-forecast", response_model=CrowdForecastResponse)
def get_crowd_forecast(
    db: Session = Depends(get_db)
):
    """
    AI Crowd Intelligence: returns current crowd level, +30m, +60m, +120m projections, and expected peak times.
    """
    return AIService.get_crowd_forecast(db=db)

@router.get("/inventory-intelligence", response_model=InventoryIntelligenceResponse)
def get_inventory_intelligence(
    meal_slot: str = Query("Lunch", pattern="^(Breakfast|Lunch|Snacks|Dinner)$"),
    admin_or_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db)
):
    """
    AI Preparation Recommendation: compares current inventory stock with predicted demand and suggests exact prep additions.
    """
    return AIService.get_inventory_intelligence(db=db, meal_slot=meal_slot)

@router.get("/waste-analytics", response_model=FoodWasteAnalyticsResponse)
def get_food_waste_analytics(
    admin_or_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db)
):
    """
    AI Waste Intelligence: tracks prepared vs sold portions, financial loss in INR, weekly trend, and AI reduction suggestions.
    """
    return AIService.get_food_waste_analytics(db=db)

@router.post("/demand-forecast", response_model=DemandForecastResponse)
@router.get("/demand-forecast", response_model=DemandForecastResponse)
@router.post("/demand-prediction", response_model=DemandForecastResponse)
@router.get("/demand-prediction", response_model=DemandForecastResponse)
def get_demand_forecast(
    target_date: Optional[date] = None,
    meal_slot: str = Query("Lunch", pattern="^(Breakfast|Lunch|Snacks|Dinner)$"),
    admin_or_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db)
):
    """AI Demand Forecasting engine incorporating admin overrides."""
    return AIService.get_demand_forecast(db=db, target_date=target_date, meal_slot=meal_slot)

@router.post("/demand-override", response_model=PredictionOverrideResponse)
def create_demand_override(
    data: PredictionOverrideCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin overrides predicted prep quantity for a dish with audit logging."""
    return AIService.create_prediction_override(db=db, admin_user_id=admin.id, data=data)

@router.get("/demand-overrides", response_model=List[PredictionOverrideResponse])
def get_all_demand_overrides(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lists recent admin prediction overrides."""
    return AIService.get_prediction_overrides(db=db)

@router.get("/demand-vs-actual", response_model=DemandVsActualResponse)
def get_demand_vs_actual(
    days: int = Query(7, ge=3, le=30),
    admin_or_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db)
):
    """Returns 7-day predicted vs actual demand points and accuracy for Chart.js visualization."""
    return AIService.get_demand_vs_actual(db=db, days=days)

@router.get("/queue-status", response_model=QueueStatusResponse)
def get_live_queue_status(
    db: Session = Depends(get_db)
):
    """Real-time crowd level, average wait minutes, active counters, and rush predictions."""
    return AIService.get_live_queue_and_crowd_status(db=db)

@router.get("/traffic-forecast")
def get_hourly_traffic_forecast():
    """Returns 24-hour hourly expected traffic curves."""
    return AIService.queue_predictor.get_hourly_forecast()
