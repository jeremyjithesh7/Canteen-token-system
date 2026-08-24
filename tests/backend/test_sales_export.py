import pytest
from fastapi.testclient import TestClient

def test_export_sales_report_csv(client: TestClient, admin_auth_headers):
    response = client.get("/api/admin/export-sales?format=csv", headers=admin_auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    content = response.text
    assert "DIGITAL CANTEEN TOKEN SYSTEM - SALES REPORT" in content
    assert "Order Number" in content
    assert "Token Number" in content
