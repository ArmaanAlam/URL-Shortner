import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.base62 import encode_base62, decode_base62

client = TestClient(app)

def test_base62_bijective_encoding():
    test_values = [0, 1, 61, 62, 125, 100000, 9999999]
    for val in test_values:
        encoded = encode_base62(val)
        decoded = decode_base62(encoded)
        assert decoded == val, f"Failed round-trip for {val}: got {decoded}"
    print("[PASS] Base62 bijective encoding verified.")

def test_modular_architecture_flow():
    # 1. Health check
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print("[PASS] Health check endpoint verified.")

    # 2. Shorten URL
    long_url = "https://backend-from-first-principle.vercel.app/"
    res = client.post("/api/shorten", json={"url": long_url})
    assert res.status_code == 201
    data = res.json()
    assert "short_key" in data
    assert data["original_url"] == long_url
    short_key = data["short_key"]
    print(f"[PASS] Shorten endpoint generated key: {short_key}")

    # 3. Deduplication (Same URL returns same key)
    res_dup = client.post("/api/shorten", json={"url": long_url})
    assert res_dup.status_code == 201
    assert res_dup.json()["short_key"] == short_key
    print("[PASS] URL deduplication verified.")

    # 4. Custom Alias
    res_custom = client.post("/api/shorten", json={
        "url": "https://github.com/DsThakurRawat/Backend-from-first-Principle",
        "custom_alias": "backend-first-principles"
    })
    assert res_custom.status_code in (201, 409)
    print("[PASS] Custom alias handling verified.")

    # 5. Redirect (302 Found)
    res_redir = client.get(f"/{short_key}", follow_redirects=False)
    assert res_redir.status_code == 302
    assert res_redir.headers["location"] == long_url
    print("[PASS] HTTP 302 redirect verified.")

    # Small pause for background async audit logging
    time.sleep(0.3)

    # 6. Analytics / Stats
    res_stats = client.get(f"/api/stats/{short_key}")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_clicks"] >= 1
    print(f"[PASS] Click analytics verified ({stats['total_clicks']} clicks recorded).")

if __name__ == "__main__":
    test_base62_bijective_encoding()
    test_modular_architecture_flow()
    print("\nALL tests against industrial-grade modular architecture passed successfully!")
