from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.schemas.counter import CounterResponse, CounterCreate, CounterUpdate
from backend.app.services.counter_service import CounterService
from backend.app.authentication.deps import get_current_admin

router = APIRouter(prefix="/api/counters", tags=["Counters"])

@router.get("/", response_model=List[CounterResponse])
def get_counters(
    only_active: bool = Query(True, description="Filter only active counters"),
    db: Session = Depends(get_db)
):
    """Returns list of canteen counters / stalls."""
    return CounterService.get_all_counters(db, only_active=only_active)

@router.get("/{counter_id}", response_model=CounterResponse)
def get_counter_detail(
    counter_id: int,
    db: Session = Depends(get_db)
):
    """Returns counter details."""
    return CounterService.get_counter_by_id(db, counter_id)

@router.post("/", response_model=CounterResponse, status_code=201)
def create_counter(
    data: CounterCreate,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Admin adds a new canteen counter."""
    return CounterService.create_counter(db, data)

@router.put("/{counter_id}", response_model=CounterResponse)
def update_counter(
    counter_id: int,
    data: CounterUpdate,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Admin updates counter settings."""
    return CounterService.update_counter(db, counter_id, data)
