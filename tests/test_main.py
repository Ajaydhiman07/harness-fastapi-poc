import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
from main import app, items_db, counter

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Reset DB state before each test."""
    items_db.clear()
    counter["id"] = 1
    yield

# ---------- Health Tests ----------

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# ---------- CRUD Tests ----------

def test_create_item():
    payload = {"name": "Widget", "description": "A test widget", "price": 9.99, "in_stock": True}
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Widget"
    assert data["price"] == 9.99

def test_get_items_empty():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []

def test_get_items():
    client.post("/items", json={"name": "A", "price": 1.0})
    client.post("/items", json={"name": "B", "price": 2.0})
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_item_by_id():
    client.post("/items", json={"name": "Widget", "price": 5.0})
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"

def test_get_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_update_item():
    client.post("/items", json={"name": "Old Name", "price": 1.0})
    response = client.put("/items/1", json={"name": "New Name", "price": 2.0, "in_stock": False})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["price"] == 2.0

def test_update_item_not_found():
    response = client.put("/items/999", json={"name": "X", "price": 1.0})
    assert response.status_code == 404

def test_delete_item():
    client.post("/items", json={"name": "To Delete", "price": 3.0})
    response = client.delete("/items/1")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]

def test_delete_item_not_found():
    response = client.delete("/items/999")
    assert response.status_code == 404
