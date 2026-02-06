from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "VeriJob AI Verification Engine is Running!"}

def test_verify_job_mock():
    # Since we are mocking, any URL should work and return the mock response from verifier.py
    response = client.post("/verify", json={"url": "https://example.com/job"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["Verified", "Unverified", "Error"]
    assert "score" in data
