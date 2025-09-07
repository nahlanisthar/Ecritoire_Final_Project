def test_samples_analyze_generate_feedback_stats(client, db_session, create_user):
    # Creating a user
    user = create_user(email="user1@example.com")

    # Uploading a writing sample
    sample_payload = {
        "title": "My Day",
        "content": "I am very happy today! The sun is bright and I feel excited about life.",
        "user_id": user.id
    }
    r = client.post("/api/samples/upload", json=sample_payload)
    assert r.status_code == 200, r.text
    sample_id = r.json()["id"]
    assert sample_id is not None

    # Analyzing samples to build style profile
    r = client.post(f"/api/samples/analyze")
    assert r.status_code == 200, r.text
    assert r.json()["success"] is True

    # Generating content (using mocked ollama)
    gen_payload = {
        "prompt": "Write a positive note about learning.",
        "user_id": user.id,
        "context": "personal"
    }
    r = client.post("/api/generate/content", json=gen_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True
    content_id = body["content_id"]
    assert isinstance(content_id, int)
    print("API Response:", r.json())

    # Submitting feedback (accepted)
    feedback_payload = {
        "content_id": content_id,
        "user_id": user.id,
        "feedback_type": "accepted",
        "modified_content": None
    }
    r = client.post("/api/generate/feedback", json=feedback_payload)
    assert r.status_code == 200, r.text
    assert r.json()["success"] is True

    # Checking if stats reflect acceptance
    r = client.get(f"/api/generate/stats")
    assert r.status_code == 200, r.text
    stats = r.json()["stats"]
    assert stats["total_generations"] >= 1

    if stats["total_generations"] == 1:
        assert stats["acceptance_rate"] == 100.0
