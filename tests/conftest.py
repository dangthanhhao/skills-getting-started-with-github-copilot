"""
Pytest configuration and fixtures for FastAPI tests.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path so we can import app
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store original state
    original_activities = {
        "Debate Team": {
            "id": 1,
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"],
        },
        "Soccer Team": {
            "id": 2,
            "description": "Competitive soccer team for intramural and regional matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["carlos@mergington.edu"],
        },
        "Swimming Club": {
            "id": 3,
            "description": "Competitive swimming and water polo",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["maya@mergington.edu"],
        },
        "Drama Club": {
            "id": 4,
            "description": "Perform in theater productions and develop acting skills",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu"],
        },
        "Art Studio": {
            "id": 5,
            "description": "Explore painting, sculpture, and digital art techniques",
            "schedule": "Mondays and Thursdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"],
        },
        "Science Club": {
            "id": 6,
            "description": "Conduct experiments and explore STEM topics through hands-on projects",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["nathan@mergington.edu"],
        },
        "Math Olympiad": {
            "id": 7,
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["priya@mergington.edu"],
        },
        "Robotics Club": {
            "id": 8,
            "description": "Build and program robots for competitions",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"],
        },
        "Chess Club": {
            "id": 9,
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "id": 10,
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "id": 11,
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)
