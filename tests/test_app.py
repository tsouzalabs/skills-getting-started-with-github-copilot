import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture(autouse=True)
def reset_activities():
    # Salva o estado original e restaura após cada teste
    original = {k: v.copy() for k, v in activities.items()}
    for k, v in original.items():
        v["participants"] = list(v["participants"])
    yield
    for k in activities:
        activities[k]["participants"] = list(original[k]["participants"])

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)

def test_signup_success():
    email = "novo@mergington.edu"
    response = client.post("/activities/Chess Club/signup?email=" + email)
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    email = activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/AtividadeInexistente/signup?email=alguem@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_remove_participant_success():
    email = activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess Club/remove?email={email}")
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

def test_remove_participant_not_found():
    response = client.post("/activities/Chess Club/remove?email=naoexiste@mergington.edu")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

def test_remove_activity_not_found():
    response = client.post("/activities/AtividadeInexistente/remove?email=alguem@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
