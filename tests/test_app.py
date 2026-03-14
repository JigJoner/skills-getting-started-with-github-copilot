def test_root_redirects_to_static_index(client):
    response = client.get("/")
    assert response.status_code == 200

    # TestClient automatically follows redirects by default. Set follow_redirects=False to inspect location.
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_includes_known_activity(client):
    response = client.get("/activities")
    assert response.status_code == 200
    payload = response.json()

    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"].startswith("Learn strategies")


def test_signup_success_and_duplicate(client):
    email = "teststudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    # duplicate signup should be rejected
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_missing_activity(client):
    response = client.post("/activities/Nonexistent signup/signup", params={"email": "a@x.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_and_errors(client):
    email = "michael@mergington.edu"

    # Successful unregister existing participant
    response = client.delete("/activities/Chess Club/participant", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    # Unregister missing participant returns 404
    response = client.delete("/activities/Chess Club/participant", params={"email": email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"

    # Unregister in missing activity returns 404
    response = client.delete("/activities/NoClub/participant", params={"email": "a@x.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
