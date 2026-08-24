from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from backend.app.models.counter import Counter
from backend.app.schemas.counter import CounterCreate, CounterUpdate

class CounterService:
    @staticmethod
    def get_all_counters(db: Session, only_active: bool = True) -> List[Counter]:
        query = db.query(Counter)
        if only_active:
            query = query.filter(Counter.is_active == True)
        return query.order_by(Counter.display_order.asc(), Counter.id.asc()).all()

    @staticmethod
    def get_counter_by_id(db: Session, counter_id: int) -> Counter:
        counter = db.query(Counter).filter(Counter.id == counter_id).first()
        if not counter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Counter not found")
        return counter

    @staticmethod
    def create_counter(db: Session, data: CounterCreate) -> Counter:
        existing = db.query(Counter).filter(Counter.code == data.code).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Counter code '{data.code}' already exists")
        
        counter = Counter(**data.dict())
        db.add(counter)
        db.commit()
        db.refresh(counter)
        return counter

    @staticmethod
    def update_counter(db: Session, counter_id: int, data: CounterUpdate) -> Counter:
        counter = CounterService.get_counter_by_id(db, counter_id)
        for key, value in data.dict(exclude_unset=True).items():
            setattr(counter, key, value)
        db.commit()
        db.refresh(counter)
        return counter
