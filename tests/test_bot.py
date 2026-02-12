from fastapi.testclient import TestClient
from app.main import app

def test_bot_greeting():
    with TestClient(app) as client:
        response = client.post(
            "/bot/greeting",
            json={"bot_name": "Jarvis", "meeting_topic": "AI Integration"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "greeting": "Hello, I am Jarvis and I will be recording this meeting about AI Integration"
        }

def test_bot_greeting_missing_field():
    with TestClient(app) as client:
        response = client.post(
            "/bot/greeting",
            json={"bot_name": "Jarvis"}
        )
        assert response.status_code == 422
