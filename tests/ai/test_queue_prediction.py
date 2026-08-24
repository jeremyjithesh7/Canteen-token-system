import pytest
from ai.queue_prediction.queue_estimator import QueuePredictor

def test_queue_density_and_crowd_level():
    predictor = QueuePredictor()

    # Empty queue
    empty_status = predictor.estimate_current_queue(active_tokens=[])
    assert empty_status["crowd_level"] == "Low"
    assert empty_status["estimated_average_wait_minutes"] <= 5

    # Busy queue (12 active orders)
    busy_tokens = [{"id": i, "status": "Waiting", "counter_number": (i % 3) + 1} for i in range(1, 13)]
    busy_status = predictor.estimate_current_queue(active_tokens=busy_tokens)
    assert busy_status["crowd_level"] in ["High", "Peak", "Moderate"]
    assert busy_status["estimated_average_wait_minutes"] > 5
    assert len(busy_status["upcoming_busy_periods"]) > 0

def test_hourly_traffic_forecast():
    predictor = QueuePredictor()
    forecast = predictor.get_hourly_forecast()
    assert len(forecast) > 0
    assert "time_label" in forecast[0]
    assert "expected_orders" in forecast[0]
    assert "congestion_level" in forecast[0]
