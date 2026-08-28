from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.app.models.food import FoodItem, Category
from backend.app.models.counter import Counter
from backend.app.models.token import Token
from backend.app.models.order import Order, OrderItem
from backend.app.models.inventory import Inventory
from backend.app.models.waste import FoodWasteLog
from backend.app.models.rating import FoodRating
from backend.app.models.ai_data import UserPreference, PredictionOverride, DemandPrediction
from backend.app.schemas.ai import (
    DemandForecastResponse,
    DemandPredictionItem,
    FoodRecommendationItem,
    QueueStatusResponse,
    PredictionOverrideCreate,
    PredictionOverrideResponse,
    DemandVsActualResponse,
    DemandVsActualPoint,
    CrowdForecastResponse,
    CrowdTimelinePoint,
    InventoryIntelligenceResponse,
    InventoryIntelligenceItem
)
from backend.app.schemas.waste import (
    FoodWasteAnalyticsResponse,
    FoodWasteItem,
    WasteDayTrend
)

from ai.demand_prediction.model import DemandPredictionModel
from ai.token_allocation.smart_allocator import SmartTokenAllocator
from ai.food_recommendation.recommender import FoodRecommender
from ai.queue_prediction.queue_estimator import QueuePredictor

class AIService:
    demand_model = DemandPredictionModel()
    token_allocator = SmartTokenAllocator()
    recommender = FoodRecommender()
    queue_predictor = QueuePredictor()

    @classmethod
    def get_demand_forecast(
        cls,
        db: Session,
        target_date: Optional[date] = None,
        meal_slot: str = "Lunch"
    ) -> DemandForecastResponse:
        target_date = target_date or (date.today() + timedelta(days=1))
        
        overrides = db.query(PredictionOverride).filter(
            PredictionOverride.prediction_date == target_date,
            PredictionOverride.meal_slot == meal_slot
        ).all()
        overrides_map = {o.food_item_id: o.override_quantity for o in overrides}

        food_items = db.query(FoodItem).join(Category).all()
        catalog = [
            {
                "id": item.id,
                "name": item.name,
                "category_slug": item.category.slug if item.category else "meals"
            }
            for item in food_items
        ]

        predictions = cls.demand_model.predict_all_menu_demand(
            food_items_catalog=catalog,
            target_date=target_date,
            meal_slot=meal_slot,
            overrides_map=overrides_map
        )

        items_pydantic = [DemandPredictionItem(**p) for p in predictions]
        total_prep = sum(p["recommended_prep_quantity"] for p in predictions)

        return DemandForecastResponse(
            forecast_date=target_date.isoformat(),
            meal_slot=meal_slot,
            total_predicted_items=len(predictions),
            total_prep_units=total_prep,
            items=items_pydantic
        )

    @classmethod
    def create_prediction_override(
        cls,
        db: Session,
        admin_user_id: int,
        data: PredictionOverrideCreate
    ) -> PredictionOverrideResponse:
        food_item = db.query(FoodItem).join(Category).filter(FoodItem.id == data.food_item_id).first()
        if not food_item:
            raise ValueError("Food item not found")

        pred = cls.demand_model.predict_item_demand(
            item_id=food_item.id,
            item_name=food_item.name,
            category_slug=food_item.category.slug if food_item.category else "meals",
            target_date=data.prediction_date,
            meal_slot=data.meal_slot
        )

        existing = db.query(PredictionOverride).filter(
            PredictionOverride.food_item_id == data.food_item_id,
            PredictionOverride.prediction_date == data.prediction_date,
            PredictionOverride.meal_slot == data.meal_slot
        ).first()

        if existing:
            existing.override_quantity = data.override_quantity
            existing.reason = data.reason
            existing.admin_user_id = admin_user_id
            db.commit()
            db.refresh(existing)
            target_override = existing
        else:
            target_override = PredictionOverride(
                food_item_id=data.food_item_id,
                prediction_date=data.prediction_date,
                meal_slot=data.meal_slot,
                original_predicted_quantity=pred["predicted_demand"],
                override_quantity=data.override_quantity,
                admin_user_id=admin_user_id,
                reason=data.reason
            )
            db.add(target_override)
            db.commit()
            db.refresh(target_override)

        return PredictionOverrideResponse(
            id=target_override.id,
            food_item_id=target_override.food_item_id,
            food_item_name=food_item.name,
            prediction_date=target_override.prediction_date,
            meal_slot=target_override.meal_slot,
            original_predicted_quantity=target_override.original_predicted_quantity,
            override_quantity=target_override.override_quantity,
            admin_user_id=target_override.admin_user_id,
            admin_name=target_override.admin_user.name if target_override.admin_user else "Admin",
            reason=target_override.reason,
            created_at=target_override.created_at
        )

    @classmethod
    def get_prediction_overrides(cls, db: Session) -> List[PredictionOverrideResponse]:
        overrides = db.query(PredictionOverride).order_by(PredictionOverride.created_at.desc()).limit(50).all()
        results = []
        for o in overrides:
            results.append(PredictionOverrideResponse(
                id=o.id,
                food_item_id=o.food_item_id,
                food_item_name=o.food_item.name if o.food_item else f"Item #{o.food_item_id}",
                prediction_date=o.prediction_date,
                meal_slot=o.meal_slot,
                original_predicted_quantity=o.original_predicted_quantity,
                override_quantity=o.override_quantity,
                admin_user_id=o.admin_user_id,
                admin_name=o.admin_user.name if o.admin_user else "Admin",
                reason=o.reason,
                created_at=o.created_at
            ))
        return results

    @classmethod
    def get_demand_vs_actual(cls, db: Session, days: int = 7) -> DemandVsActualResponse:
        end_date = date.today()
        food_items = db.query(FoodItem).limit(6).all()
        data_points = []
        total_variance_pct = 0.0
        points_with_actuals = 0

        for day_offset in range(days, 0, -1):
            cur_date = end_date - timedelta(days=day_offset)
            date_str = cur_date.strftime("%b %d")

            for item in food_items:
                cat_slug = item.category.slug if item.category else "meals"
                pred = cls.demand_model.predict_item_demand(
                    item_id=item.id,
                    item_name=item.name,
                    category_slug=cat_slug,
                    target_date=cur_date,
                    meal_slot="Lunch"
                )
                predicted_qty = pred["predicted_demand"]

                # Query actual recorded orders for this dish on this date from PostgreSQL
                day_start = datetime.combine(cur_date, datetime.min.time())
                day_end = datetime.combine(cur_date, datetime.max.time())
                actual_qty = db.query(func.coalesce(func.sum(OrderItem.quantity), 0)).join(Order).filter(
                    OrderItem.food_item_id == item.id,
                    Order.created_at >= day_start,
                    Order.created_at <= day_end,
                    Order.status != "Cancelled"
                ).scalar() or 0

                variance = actual_qty - predicted_qty
                if actual_qty > 0 and predicted_qty > 0:
                    acc = max(0.0, min(100.0, 100.0 - abs(variance) / predicted_qty * 100.0))
                    total_variance_pct += acc
                    points_with_actuals += 1
                else:
                    acc = 0.0

                data_points.append(DemandVsActualPoint(
                    date=date_str,
                    food_item_id=item.id,
                    food_item_name=item.name,
                    predicted_demand=predicted_qty,
                    actual_demand=actual_qty,
                    variance=variance,
                    accuracy_percentage=round(acc, 1)
                ))

        overall_accuracy = round(total_variance_pct / max(1, points_with_actuals), 1) if points_with_actuals > 0 else 0.0
        return DemandVsActualResponse(
            period_days=days,
            overall_accuracy=overall_accuracy,
            data=data_points
        )

    @classmethod
    def get_food_recommendations(
        cls,
        db: Session,
        user_id: int,
        top_n: int = 4
    ) -> List[FoodRecommendationItem]:
        all_items = db.query(FoodItem).join(Category).all()
        catalog = []
        for i in all_items:
            avg_rating = db.query(func.avg(FoodRating.rating)).filter(FoodRating.food_item_id == i.id).scalar()
            catalog.append({
                "id": i.id,
                "name": i.name,
                "category_id": i.category_id,
                "category_name": i.category.name if i.category else "Dish",
                "category_slug": i.category.slug if i.category else "meals",
                "price": i.price,
                "is_veg": i.is_veg,
                "is_available": i.is_available,
                "prep_time_minutes": i.prep_time_minutes,
                "image_url": i.image_url,
                "protein": i.protein,
                "average_rating": round(float(avg_rating), 1) if avg_rating else 0.0
            })

        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        pref_dict = {
            "is_veg_only": pref.is_veg_only if pref else False,
            "favorite_category_id": pref.favorite_category_id if pref else None
        }

        orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(10).all()
        history = []
        for o in orders:
            history.append({
                "id": o.id,
                "items": [{"food_item_id": oi.food_item_id, "quantity": oi.quantity} for oi in o.items]
            })

        recs = cls.recommender.recommend(
            user_id=user_id,
            all_food_items=catalog,
            user_order_history=history,
            user_preferences=pref_dict,
            top_n=top_n
        )
        return [FoodRecommendationItem(**r) for r in recs]

    @classmethod
    def get_live_queue_and_crowd_status(cls, db: Session) -> QueueStatusResponse:
        active_tokens = db.query(Token).filter(Token.status.in_(["Waiting", "Preparing"])).all()
        tokens_list = [
            {
                "id": t.id,
                "status": t.status,
                "counter_number": t.counter_number or 1,
                "estimated_wait_minutes": t.estimated_wait_minutes
            }
            for t in active_tokens
        ]

        estimation = cls.queue_predictor.estimate_current_queue(tokens_list)
        return QueueStatusResponse(**estimation)

    @classmethod
    def get_crowd_forecast(cls, db: Session) -> CrowdForecastResponse:
        active_count = db.query(Token).filter(Token.status.in_(["Waiting", "Preparing"])).count()
        now = datetime.now()
        hour = now.hour

        # Base current state
        if active_count <= 2:
            current_crowd = "LOW"
            curr_wait = 4
        elif active_count <= 6:
            current_crowd = "MODERATE"
            curr_wait = 8
        elif active_count <= 12:
            current_crowd = "HIGH"
            curr_wait = 15
        else:
            current_crowd = "PEAK"
            curr_wait = 22

        # 30m, 60m, 120m projection based on time of day rush
        if 11 <= hour < 14: # Lunch rush build-up
            f30 = "HIGH"
            f60 = "PEAK"
            f120 = "LOW"
            peak_time = "01:15 PM"
            peak_level = "PEAK (Heavy Rush)"
            rec = "High queue expected during lunch slot. Use Pre-Order or order before 12:45 PM for rapid pickup."
        elif 16 <= hour < 18: # Evening snacks rush
            f30 = "HIGH"
            f60 = "MODERATE"
            f120 = "LOW"
            peak_time = "05:15 PM"
            peak_level = "HIGH (Tea & Snacks)"
            rec = "Evening tea rush active at Counter 3. Filter Coffee orders dispatched in under 4 minutes."
        elif 8 <= hour < 10: # Breakfast rush
            f30 = "HIGH"
            f60 = "MODERATE"
            f120 = "LOW"
            peak_time = "09:15 AM"
            peak_level = "HIGH (Morning Tiffin)"
            rec = "Counter 1 (Tiffin) has brisk flow. Steamed Idlis & Vada ready instantly."
        else:
            f30 = "MODERATE"
            f60 = "LOW"
            f120 = "LOW"
            peak_time = "01:00 PM"
            peak_level = "MODERATE"
            rec = "Normal smooth traffic. Average wait time across all 3 counters is currently under 6 minutes."

        timeline = [
            CrowdTimelinePoint(
                time_offset="NOW",
                time_label=now.strftime("%I:%M %p"),
                crowd_level=current_crowd,
                crowd_color="green" if current_crowd == "LOW" else ("yellow" if current_crowd == "MODERATE" else ("orange" if current_crowd == "HIGH" else "red")),
                estimated_wait_minutes=curr_wait,
                expected_order_volume=max(3, active_count)
            ),
            CrowdTimelinePoint(
                time_offset="+30m",
                time_label=(now + timedelta(minutes=30)).strftime("%I:%M %p"),
                crowd_level=f30,
                crowd_color="orange" if f30 in ["HIGH", "PEAK"] else "yellow",
                estimated_wait_minutes=14 if f30 == "HIGH" else (20 if f30 == "PEAK" else 7),
                expected_order_volume=18 if f30 == "PEAK" else (12 if f30 == "HIGH" else 6)
            ),
            CrowdTimelinePoint(
                time_offset="+60m",
                time_label=(now + timedelta(minutes=60)).strftime("%I:%M %p"),
                crowd_level=f60,
                crowd_color="red" if f60 == "PEAK" else ("orange" if f60 == "HIGH" else "green"),
                estimated_wait_minutes=22 if f60 == "PEAK" else (12 if f60 == "HIGH" else 5),
                expected_order_volume=24 if f60 == "PEAK" else (14 if f60 == "HIGH" else 4)
            ),
            CrowdTimelinePoint(
                time_offset="+120m",
                time_label=(now + timedelta(minutes=120)).strftime("%I:%M %p"),
                crowd_level=f120,
                crowd_color="green" if f120 == "LOW" else "yellow",
                estimated_wait_minutes=5 if f120 == "LOW" else 8,
                expected_order_volume=4
            ),
        ]

        return CrowdForecastResponse(
            current_crowd=current_crowd,
            current_wait_minutes=curr_wait,
            forecast_30m=f30,
            forecast_60m=f60,
            forecast_120m=f120,
            expected_peak_time=peak_time,
            expected_peak_level=peak_level,
            recommendation=rec,
            timeline=timeline
        )

    @classmethod
    def get_inventory_intelligence(cls, db: Session, meal_slot: str = "Lunch") -> InventoryIntelligenceResponse:
        forecast = cls.get_demand_forecast(db, target_date=date.today(), meal_slot=meal_slot)
        items_intel = []
        high_demand_count = 0
        total_prep = 0

        for p in forecast.items:
            inv = db.query(Inventory).filter(Inventory.food_item_id == p.food_item_id).first()
            current_stock = inv.current_stock if inv else 15

            # Calculate recommended additional prep
            needed = max(0, p.recommended_prep_quantity - current_stock)
            total_prep += needed

            if p.predicted_demand > current_stock * 1.5:
                status = "HIGH DEMAND"
                status_color = "red"
                high_demand_count += 1
            elif p.predicted_demand > current_stock:
                status = "MODERATE"
                status_color = "orange"
            elif current_stock >= p.predicted_demand * 1.5:
                status = "SURPLUS"
                status_color = "blue"
            else:
                status = "ADEQUATE"
                status_color = "green"

            items_intel.append(InventoryIntelligenceItem(
                food_item_id=p.food_item_id,
                name=p.name,
                category=p.category,
                current_stock=current_stock,
                predicted_demand=p.predicted_demand,
                recommended_preparation=needed,
                status=status,
                status_color=status_color,
                has_override=p.has_admin_override,
                override_quantity=p.override_quantity
            ))

        # Sort: High demand first, then by needed preparation descending
        items_intel.sort(key=lambda x: (0 if x.status == "HIGH DEMAND" else (1 if x.status == "MODERATE" else 2), -x.recommended_preparation))

        return InventoryIntelligenceResponse(
            generated_at=datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            meal_slot=meal_slot,
            total_items_analyzed=len(items_intel),
            total_prep_recommended=total_prep,
            high_demand_count=high_demand_count,
            items=items_intel
        )

    @classmethod
    def get_food_waste_analytics(cls, db: Session) -> FoodWasteAnalyticsResponse:
        logs = db.query(FoodWasteLog).order_by(FoodWasteLog.log_date.desc()).limit(150).all()

        if not logs:
            return FoodWasteAnalyticsResponse(
                total_prepared_portions=0,
                total_sold_portions=0,
                total_waste_portions=0,
                overall_waste_percentage=Decimal("0.0"),
                total_financial_loss_inr=Decimal("0.0"),
                most_wasted_dishes=[],
                weekly_trend=[],
                ai_waste_reduction_suggestions=[
                    "No food waste logs recorded yet. Waste analytics will calibrate automatically as kitchen preparation logs and unsold inventory are recorded."
                ]
            )

        total_prep = sum(l.prepared_quantity for l in logs)
        total_sold = sum(l.sold_quantity for l in logs)
        total_waste = sum(l.waste_quantity for l in logs)
        total_loss = sum(float(l.waste_cost_inr) for l in logs)
        overall_waste_pct = round((total_waste / max(1, total_prep)) * 100.0, 2)

        # Most wasted dishes grouped by food_item_id
        waste_by_food_map = {}
        for l in logs:
            fid = l.food_item_id
            if fid not in waste_by_food_map:
                name = l.food_item.name if l.food_item else f"Dish #{fid}"
                cat = l.food_item.category.name if (l.food_item and l.food_item.category) else "Food"
                waste_by_food_map[fid] = {
                    "food_item_id": fid,
                    "name": name,
                    "category": cat,
                    "prep": 0,
                    "sold": 0,
                    "waste": 0,
                    "leftover": 0,
                    "cost": 0.0,
                    "reason": l.waste_reason
                }
            waste_by_food_map[fid]["prep"] += l.prepared_quantity
            waste_by_food_map[fid]["sold"] += l.sold_quantity
            waste_by_food_map[fid]["waste"] += l.waste_quantity
            waste_by_food_map[fid]["leftover"] += l.leftover_quantity
            waste_by_food_map[fid]["cost"] += float(l.waste_cost_inr)

        most_wasted_list = []
        for fid, d in waste_by_food_map.items():
            wpct = round((d["waste"] / max(1, d["prep"])) * 100.0, 1)
            most_wasted_list.append(FoodWasteItem(
                food_item_id=fid,
                name=d["name"],
                category=d["category"],
                prepared_quantity=d["prep"],
                sold_quantity=d["sold"],
                leftover_quantity=d["leftover"],
                waste_quantity=d["waste"],
                waste_percentage=wpct,
                waste_cost_inr=round(d["cost"], 2),
                waste_reason=d["reason"]
            ))

        most_wasted_list.sort(key=lambda x: x.waste_quantity, reverse=True)

        # Weekly trend (last 7 days)
        trend_map = {}
        for l in logs:
            d_str = l.log_date.isoformat()
            if d_str not in trend_map:
                trend_map[d_str] = {
                    "date": d_str,
                    "day_name": l.log_date.strftime("%a (%b %d)"),
                    "prep": 0,
                    "sold": 0,
                    "waste": 0,
                    "loss": 0.0
                }
            trend_map[d_str]["prep"] += l.prepared_quantity
            trend_map[d_str]["sold"] += l.sold_quantity
            trend_map[d_str]["waste"] += l.waste_quantity
            trend_map[d_str]["loss"] += float(l.waste_cost_inr)

        sorted_trends = sorted(trend_map.values(), key=lambda x: x["date"])
        weekly_trends = []
        for t in sorted_trends[-7:]:
            pct = round((t["waste"] / max(1, t["prep"])) * 100.0, 1)
            weekly_trends.append(WasteDayTrend(
                date=t["date"],
                day_name=t["day_name"],
                total_prepared=t["prep"],
                total_sold=t["sold"],
                total_wasted=t["waste"],
                waste_percentage=pct,
                loss_inr=round(t["loss"], 2)
            ))

        # AI/Statistical Suggestions
        suggestions = [
            "Reduce preparation buffer for items with high unsold ratios.",
            "Schedule express item prep during peak hours (12:30-01:30 PM) to minimize food holding time.",
            "Audit portion sizing across high-spoilage items."
        ]

        return FoodWasteAnalyticsResponse(
            total_prepared_portions=total_prep,
            total_sold_portions=total_sold,
            total_waste_portions=total_waste,
            overall_waste_percentage=overall_waste_pct,
            total_financial_loss_inr=round(total_loss, 2),
            most_wasted_dishes=most_wasted_list[:8],
            weekly_trend=weekly_trends,
            ai_waste_reduction_suggestions=suggestions
        )
