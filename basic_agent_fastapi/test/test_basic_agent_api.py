import pytest
from fastapi.testclient import TestClient
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, runner, session_service
from greeting_agent.prompt import FINAL_RESPONSE
from google.genai import types

client = TestClient(app)

# ----------------------------------
# Test 1: Health endpoint
# ----------------------------------
@pytest.mark.asyncio
async def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status_code"] == 200
    assert json_resp["status_message"] ==  "ok"



# ------------------------------------------
# Test 2: Query endpoint with final response
# ------------------------------------------

@pytest.mark.asyncio
async def test_query_with_final_response(monkeypatch):
    test_query = "Hello"
    expected_response = "Mocked response"

    # Mock session object
    class DummySession:
        id = "dummy_session_id"
    
    # Fake session object
    async def mock_create_session(user_id, app_name):
        return DummySession()
    
    class DummyEvent:
        final = True
        content = types.Content(
            role="assistant",
            parts=[types.Part(text=expected_response)]
        )        

    # Fake runner (yields one final event)
    async def mock_run_async(new_message, user_id, session_id):
        yield DummyEvent()

    # Replace real functions with fakes
    monkeypatch.setattr(session_service, "create_session", mock_create_session)
    monkeypatch.setattr(runner, "run_async", mock_run_async)

    # Call the API
    response = client.post("/greet", json={"query": test_query})
    assert response.status_code == 200
    json_resp = response.json()
    print(json_resp)
    assert json_resp["response"] == expected_response