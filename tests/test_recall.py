def test_recall_finds_laptop(client):
    client.post("/api/imports/sample")
    r = client.post("/api/recall", json={"question": "Why did I choose the gray laptop?"})
    data = r.json()
    assert not data["insufficient_evidence"]
    assert data["results"][0]["conversation_title"] == "Laptop choice"

def test_recall_no_match(client):
    client.post("/api/imports/sample")
    r = client.post("/api/recall", json={"question": "What color was the house?"})
    assert r.json()["insufficient_evidence"] is True

def test_recall_punctuation_only(client):
    r = client.post("/api/recall", json={"question": "!!!"})
    assert r.status_code == 200
    assert r.json()["insufficient_evidence"] is True