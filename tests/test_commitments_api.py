def _detect(client):
    client.post("/api/imports/sample")
    return client.post("/api/commitments/detect").json()


def test_detect_is_idempotent(client):
    first = _detect(client)
    assert first["new_candidates"] >= 1
    second = client.post("/api/commitments/detect").json()
    assert second["new_candidates"] == 0


def test_candidates_start_pending_and_ledger_empty(client):
    _detect(client)
    assert len(client.get("/api/commitments/candidates").json()) >= 1
    assert client.get("/api/commitments").json() == []


def test_approve_creates_one_ledger_row_and_cannot_repeat(client):
    _detect(client)
    cid = client.get("/api/commitments/candidates").json()[0]["id"]
    r = client.post(f"/api/commitments/candidates/{cid}/approve", json={})
    assert r.status_code == 200
    assert client.post(f"/api/commitments/candidates/{cid}/approve", json={}).status_code == 409
    assert len(client.get("/api/commitments").json()) == 1


def test_rejected_candidate_does_not_return(client):
    _detect(client)
    cid = client.get("/api/commitments/candidates").json()[0]["id"]
    client.post(f"/api/commitments/candidates/{cid}/reject")
    client.post("/api/commitments/detect")
    pending_ids = [c["id"] for c in client.get("/api/commitments/candidates").json()]
    assert cid not in pending_ids
    assert client.get("/api/commitments").json() == []