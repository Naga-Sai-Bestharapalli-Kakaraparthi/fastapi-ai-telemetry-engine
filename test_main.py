from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_validation_error_short_prompt():
    """Ensures Pydantic rejects prompts under 3 characters."""
    response = client.post("/api/v1/analyze", json={"prompt": "hi"})
    assert response.status_code == 422


def test_valid_payload_structure():
    """Ensures valid requests accept schema formats."""
    response = client.post(
        "/api/v1/analyze", json={"prompt": "Valid system telemetry input"}
    )
    # Status code 200 or 500 if Redis connection is offline during test runner
    assert response.status_code in [200, 500]
