import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

DEFAULT_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: reset in-memory activities at start of each test
    activities.clear()
    activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))


@pytest.fixture
def client():
    # Arrange: FastAPI test client
    return TestClient(app)


def test_get_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_for_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Programming Class"
    existing_email = "emma@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400


def test_unregister_participant_removes_participant(client):
    # Arrange
    activity_name = "Gym Class"
    existing_email = "john@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_activity_name}/participants", params={"email": existing_email})

    # Assert
    assert response.status_code == 200
    assert existing_email not in activities[activity_name]["participants"]


def test_unregister_unknown_participant_returns_404(client):
    # Arrange
    activity_name = "Gym Class"
    non_participant_email = "nosuchuser@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_activity_name}/participants", params={"email": non_participant_email})

    # Assert
    assert response.status_code == 404
