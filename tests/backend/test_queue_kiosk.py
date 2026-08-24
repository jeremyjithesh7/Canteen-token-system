import pytest
from fastapi.testclient import TestClient

def test_kiosk_live_board_feed(client: TestClient):
    response = client.get("/api/tokens/kiosk/live")
    assert response.status_code == 200
    data = response.json()
    assert "counters" in data
    assert "crowd_level" in data
    assert "estimated_wait_minutes" in data
    assert len(data["counters"]) >= 3

    # Check counter structure
    for counter in data["counters"]:
        assert "counter_id" in counter
        assert "counter_name" in counter
        assert "counter_code" in counter
        assert "station_type" in counter
        assert "next_up" in counter
