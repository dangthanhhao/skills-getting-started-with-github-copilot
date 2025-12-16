"""
Tests for the FastAPI activities endpoints.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all activities are returned
        assert len(data) == 11
        assert "Debate Team" in data
        assert "Soccer Team" in data
        assert "Programming Class" in data

    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that activities have correct data structure."""
        response = client.get("/activities")
        data = response.json()
        
        # Check a specific activity structure
        debate_team = data["Debate Team"]
        assert "id" in debate_team
        assert "description" in debate_team
        assert "schedule" in debate_team
        assert "max_participants" in debate_team
        assert "participants" in debate_team
        
        # Verify values
        assert debate_team["id"] == 1
        assert debate_team["max_participants"] == 15
        assert isinstance(debate_team["participants"], list)

    def test_get_activities_includes_initial_participants(self, client, reset_activities):
        """Test that activities include initial participants."""
        response = client.get("/activities")
        data = response.json()
        
        # Debate Team should have alex@mergington.edu
        assert "alex@mergington.edu" in data["Debate Team"]["participants"]
        
        # Robotics Club should have two participants
        assert len(data["Robotics Club"]["participants"]) == 2
        assert "james@mergington.edu" in data["Robotics Club"]["participants"]
        assert "sarah@mergington.edu" in data["Robotics Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_id}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/1/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up newstudent@mergington.edu" in data["message"]
        assert "Debate Team" in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity."""
        # First signup
        client.post("/activities/1/signup?email=newstudent@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        
        assert "newstudent@mergington.edu" in data["Debate Team"]["participants"]

    def test_signup_to_nonexistent_activity(self, client, reset_activities):
        """Test signup to an activity that doesn't exist."""
        response = client.post(
            "/activities/999/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signup fails when student is already registered."""
        # alex@mergington.edu is already in Debate Team
        response = client.post(
            "/activities/1/signup?email=alex@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"

    def test_signup_multiple_students_to_same_activity(self, client, reset_activities):
        """Test that multiple students can signup to the same activity."""
        # Sign up first student
        response1 = client.post(
            "/activities/1/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/1/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are added
        response = client.get("/activities")
        data = response.json()
        participants = data["Debate Team"]["participants"]
        
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert "alex@mergington.edu" in participants  # Original participant

    def test_signup_same_student_to_different_activities(self, client, reset_activities):
        """Test that same student can signup to multiple activities."""
        student_email = "student@mergington.edu"
        
        # Sign up to activity 1
        response1 = client.post(f"/activities/1/signup?email={student_email}")
        assert response1.status_code == 200
        
        # Sign up to activity 2
        response2 = client.post(f"/activities/2/signup?email={student_email}")
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        
        assert student_email in data["Debate Team"]["participants"]
        assert student_email in data["Soccer Team"]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_id}/unregister endpoint."""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity."""
        # alex@mergington.edu is initially in Debate Team
        response = client.post(
            "/activities/1/unregister?email=alex@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered alex@mergington.edu" in data["message"]
        assert "Debate Team" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        # Unregister
        client.post("/activities/1/unregister?email=alex@mergington.edu")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" not in data["Debate Team"]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from an activity that doesn't exist."""
        response = client.post(
            "/activities/999/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test that unregister fails when student is not registered."""
        response = client.post(
            "/activities/1/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"

    def test_signup_then_unregister_then_signup_again(self, client, reset_activities):
        """Test signup, unregister, and signup again flow."""
        email = "student@mergington.edu"
        
        # Initial signup
        response1 = client.post(f"/activities/1/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(f"/activities/1/unregister?email={email}")
        assert response2.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Debate Team"]["participants"]
        
        # Sign up again
        response3 = client.post(f"/activities/1/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify signed up again
        response = client.get("/activities")
        data = response.json()
        assert email in data["Debate Team"]["participants"]

    def test_unregister_from_activity_with_multiple_participants(self, client, reset_activities):
        """Test unregister from activity that has multiple participants."""
        # Robotics Club has 2 initial participants
        response = client.post(
            "/activities/8/unregister?email=james@mergington.edu"
        )
        
        assert response.status_code == 200
        
        # Verify james was removed but sarah remains
        response = client.get("/activities")
        data = response.json()
        
        assert "james@mergington.edu" not in data["Robotics Club"]["participants"]
        assert "sarah@mergington.edu" in data["Robotics Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
