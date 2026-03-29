"""
FastAPI tests for Mergington High School Activities API.

Uses AAA pattern (Arrange-Act-Assert) and a fixture to isolate global state.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_activities():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    before = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert activities[activity_name]["participants"][-1] == new_email
    assert len(activities[activity_name]["participants"]) == before + 1
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Already signed up"


def test_signup_full_activity_returns_400():
    # Arrange
    activity_name = "Chess Club"
    activity = activities[activity_name]
    max_participants = activity["max_participants"]
    activity["participants"] = [f"u{i}@mergington.edu" for i in range(max_participants)]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "full@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_delete_participant_removes_participant():
    # Arrange
    activity_name = "Tennis Club"
    existing = activities[activity_name]["participants"][0]
    before = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": existing},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {existing} from {activity_name}"
    assert len(activities[activity_name]["participants"]) == before - 1
    assert existing not in activities[activity_name]["participants"]


def test_delete_participant_not_found_returns_404():
    # Arrange
    activity_name = "Tennis Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": "not.exists@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
