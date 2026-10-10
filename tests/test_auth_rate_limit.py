def test_login_rate_limit(client):
    payload = {
        "email": "invalid@example.com",
        "password": "invalid-password",
    }

    for _ in range(5):
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 429


def test_register_rate_limit(client):
    for _ in range(3):
        response = client.post("/auth/register", json={})
        assert response.status_code == 400

    response = client.post("/auth/register", json={})

    assert response.status_code == 429
