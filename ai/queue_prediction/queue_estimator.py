"""
Queue and Crowd Density Prediction Engine
Predicts live queue depth, wait times, crowd levels, and hourly rush patterns.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, time

class QueuePredictor:
    """
    Queue analysis and busy period forecasting system.
    """

    HOURLY_TRAFFIC_PROFILE = {
        7: {"expected_orders": 8, "congestion": "Low", "wait_multiplier": 0.8},
        8: {"expected_orders": 35, "congestion": "Moderate", "wait_multiplier": 1.1},
        9: {"expected_orders": 65, "congestion": "High", "wait_multiplier": 1.4},
        10: {"expected_orders": 25, "congestion": "Low", "wait_multiplier": 0.9},
        11: {"expected_orders": 30, "congestion": "Moderate", "wait_multiplier": 1.0},
        12: {"expected_orders": 95, "congestion": "Peak", "wait_multiplier": 1.7},
        13: {"expected_orders": 115, "congestion": "Peak", "wait_multiplier": 1.8},
        14: {"expected_orders": 50, "congestion": "Moderate", "wait_multiplier": 1.2},
        15: {"expected_orders": 20, "congestion": "Low", "wait_multiplier": 0.8},
        16: {"expected_orders": 60, "congestion": "High", "wait_multiplier": 1.3},
        17: {"expected_orders": 75, "congestion": "High", "wait_multiplier": 1.5},
        18: {"expected_orders": 35, "congestion": "Moderate", "wait_multiplier": 1.0},
        19: {"expected_orders": 45, "congestion": "Moderate", "wait_multiplier": 1.1},
        20: {"expected_orders": 25, "congestion": "Low", "wait_multiplier": 0.8},
        21: {"expected_orders": 10, "congestion": "Low", "wait_multiplier": 0.7}
    }

    BUSY_WINDOWS = [
        {"name": "Morning Breakfast Rush", "start": "08:30", "end": "09:45", "level": "High", "advice": "Pre-order 15 mins ahead for fast pickup"},
        {"name": "Prime Lunch Peak", "start": "12:15", "end": "14:00", "level": "Peak", "advice": "High kitchen volume — collect via Counter 1 & 2"},
        {"name": "Evening Tea & Snacks Surge", "start": "16:15", "end": "17:30", "level": "High", "advice": "Express items (Chai/Samosa) available instantly at Counter 3"},
        {"name": "Dinner Hours", "start": "19:30", "end": "20:45", "level": "Moderate", "advice": "Smooth flow and low waiting times"}
    ]

    def __init__(self):
        pass

    def get_crowd_level(self, queue_depth: int) -> str:
        """Categorizes queue depth into semantic crowd level."""
        if queue_depth <= 3:
            return "Low"
        elif queue_depth <= 8:
            return "Moderate"
        elif queue_depth <= 15:
            return "High"
        else:
            return "Peak"

    def estimate_current_queue(
        self,
        active_tokens: List[Dict[str, Any]],
        counters_count: int = 3
    ) -> Dict[str, Any]:
        """
        Estimates real-time canteen queue depth, average wait, and crowd status.
        """
        waiting_tokens = [t for t in active_tokens if t.get("status") == "Waiting"]
        preparing_tokens = [t for t in active_tokens if t.get("status") == "Preparing"]
        total_active = len(waiting_tokens) + len(preparing_tokens)

        # Counter-specific breakdown (string keys for JSON serialization)
        counter_queues = {str(c): 0 for c in range(1, counters_count + 1)}
        for t in waiting_tokens + preparing_tokens:
            c = str(t.get("counter_number", 1))
            if c in counter_queues:
                counter_queues[c] += 1
            else:
                counter_queues["1"] += 1

        current_hour = datetime.now().hour
        profile = self.HOURLY_TRAFFIC_PROFILE.get(current_hour, {"expected_orders": 30, "congestion": "Moderate", "wait_multiplier": 1.0})
        
        # Calculate dynamic average wait
        if total_active == 0:
            avg_wait = 5
        else:
            avg_wait = int(round((total_active * 3.2 / max(1, counters_count)) * profile["wait_multiplier"]))
            avg_wait = max(4, min(45, avg_wait))

        crowd_level = self.get_crowd_level(total_active)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_active_orders": total_active,
            "waiting_count": len(waiting_tokens),
            "preparing_count": len(preparing_tokens),
            "estimated_average_wait_minutes": avg_wait,
            "crowd_level": crowd_level,
            "active_counters": counters_count,
            "counter_breakdown": counter_queues,
            "confidence_score": 0.94,
            "upcoming_busy_periods": self.BUSY_WINDOWS
        }

    def get_hourly_forecast(self) -> List[Dict[str, Any]]:
        """Provides full-day hourly queue and crowd density predictions for charts."""
        forecast = []
        for hour, data in sorted(self.HOURLY_TRAFFIC_PROFILE.items()):
            time_label = f"{hour:02d}:00"
            estimated_wait = int(round((data["expected_orders"] * 0.22) * data["wait_multiplier"]))
            forecast.append({
                "hour": hour,
                "time_label": time_label,
                "expected_orders": data["expected_orders"],
                "congestion_level": data["congestion"],
                "predicted_wait_minutes": max(3, estimated_wait)
            })
        return forecast
