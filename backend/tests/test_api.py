import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}

def test_samples_endpoint():
    response = client.get("/samples")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert any(s["category"] == "Safe" for s in data)
    assert any(s["category"] == "Rude" for s in data)
    assert any(s["category"] == "Threat" for s in data)

def test_analyze_safe_message():
    response = client.post("/analyze", json={"text": "Could you please review the pull request when you have time? Thanks!"})
    assert response.status_code == 200
    data = response.json()
    assert data["toxicity_score"] < 30.0
    assert data["label"] == "Safe"
    assert data["tone"] == "Polite"
    assert "categories" in data
    assert data["categories"]["toxic"] < 30.0

def test_analyze_tone_consistency_rule():
    # Rude text that has low toxicity must NOT be marked Safe
    response = client.post("/analyze", json={"text": "Stop asking basic questions and read the documentation first."})
    assert response.status_code == 200
    data = response.json()
    assert data["tone"] == "Rude"
    # Even if toxicity is low, status badge must never say "Safe"
    assert data["label"] == "Caution"
    assert "rude" in data["explanation"].lower()

def test_analyze_toxic_message():
    response = client.post("/analyze", json={"text": "You are an absolute idiot and a complete moron."})
    assert response.status_code == 200
    data = response.json()
    assert data["toxicity_score"] > 60.0
    assert data["label"] == "Toxic"
    assert len(data["flagged_tokens"]) > 0

def test_analyze_length_validation():
    # Over 1000 characters should return 422 or 400
    long_text = "a" * 1005
    response = client.post("/analyze", json={"text": long_text})
    assert response.status_code in [400, 422]

def test_rewrite_modes():
    modes = ["Constructive", "Professional", "Friendly", "Neutral"]
    test_text = "Your code is completely wrong and makes no sense at all."
    for mode in modes:
        response = client.post("/rewrite", json={"text": test_text, "mode": mode})
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == mode
        assert data["rewrite"].strip().lower() != test_text.strip().lower()
        assert data["similarity"] >= 0.60
        assert data["new_toxicity_score"] < 25.0

def test_conversations_flow():
    chat_sample = """Alice: Hey team, we need to finalize the deployment plan.
Bob: Stop asking basic questions and read the documentation first.
Charlie: Wow Bob, you are an absolute idiot.
Alice: Let's please keep our discussion professional and constructive."""
    response = client.post("/conversations", json={"chat_text": chat_sample, "title": "Sprint Retrospective"})
    assert response.status_code == 200
    data = response.json()
    assert data["message_count"] == 4
    assert len(data["messages"]) == 4
    assert data["most_toxic_speaker"] in ["Charlie", "Bob"]
    assert "escalation_trend" in data

    conv_id = data["id"]
    get_res = client.get(f"/conversations/{conv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == conv_id

def test_insights_endpoint():
    response = client.get("/insights")
    assert response.status_code == 200
    data = response.json()
    assert "total_analyzed" in data
    assert "avg_toxicity" in data
    assert "category_distribution" in data
    assert "tone_distribution" in data
    assert "top_flagged_words" in data

