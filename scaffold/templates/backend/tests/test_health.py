def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    # status 可能是 "ok" 或 "degraded"（取决于数据库是否可用）
    assert data["status"] in ("ok", "degraded")
