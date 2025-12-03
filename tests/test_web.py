from fastapi.testclient import TestClient
from src.web.app import app
from src.database import Base, init_db, get_db, SessionLocal, engine

# Override dependency for DB if needed, but using the main one with a different URL for testing is better.
# For MVP speed, we will just use the TestClient which will use the app's DB configuration.
# Ideally we'd use an override_dependency with an in-memory SQLite.

client = TestClient(app)

def test_dashboard_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "VibeBot" in response.text

def test_scout_page_loads():
    response = client.get("/scout")
    assert response.status_code == 200
    assert "Scout for Content" in response.text

# We won't test the actual POST /scout trigger extensively because it spawns a background task 
# and calls external APIs (unless we mock them), but we can check if it redirects.

def test_scout_submission_redirects():
    response = client.post("/scout", data={"platform": "reddit", "limit": 1})
    # 303 See Other is standard for redirect after POST
    # TestClient follows redirects by default? No, usually not unless configured.
    # Starlette/FastAPI TestClient follows redirects by default in recent versions.
    # But let's check history or final URL.
    assert response.status_code == 200 # It followed redirect to /interactions
    assert "Archived Interactions" in response.text

