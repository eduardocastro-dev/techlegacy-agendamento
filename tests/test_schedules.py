def test_create_schedule(client, auth_headers, establishment):
    response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 0,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["establishment_id"] == establishment
    assert data["weekday"] == 0
    assert data["opening_time"] == "08:00"
    assert data["closing_time"] == "18:00"
    assert data["active"] is True


def test_create_schedule_invalid_weekday(client, auth_headers):
    response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 7,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"


def test_create_schedule_invalid_time(client, auth_headers):
    response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 0,
            "opening_time": "18:00",
            "closing_time": "08:00",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert data["details"]["closing_time"] == "Must be later than opening_time"


def test_create_duplicate_schedule(client, auth_headers):
    payload = {
        "weekday": 0,
        "opening_time": "08:00",
        "closing_time": "18:00",
    }

    first = client.post(
        "/schedules",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/schedules",
        headers=auth_headers,
        json=payload,
    )

    assert second.status_code == 409

    data = second.get_json()

    assert data["error"] == "Schedule already exists for this weekday"


def test_list_schedules(client, auth_headers):
    client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 2,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 0,
            "opening_time": "09:00",
            "closing_time": "17:00",
        },
    )

    response = client.get(
        "/schedules",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["weekday"] == 0
    assert data[1]["weekday"] == 2


def test_get_schedule(client, auth_headers):
    create_response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 0,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert create_response.status_code == 201

    schedule_id = create_response.get_json()["id"]

    response = client.get(
        f"/schedules/{schedule_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == schedule_id


def test_update_schedule(client, auth_headers):
    create_response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 0,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert create_response.status_code == 201

    schedule_id = create_response.get_json()["id"]

    response = client.put(
        f"/schedules/{schedule_id}",
        headers=auth_headers,
        json={
            "opening_time": "09:00",
            "closing_time": "17:00",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["opening_time"] == "09:00"
    assert data["closing_time"] == "17:00"


def test_delete_schedule(client, auth_headers):
    create_response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": 0,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert create_response.status_code == 201

    schedule_id = create_response.get_json()["id"]

    response = client.delete(
        f"/schedules/{schedule_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response = client.get(
        f"/schedules/{schedule_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_create_schedule_without_auth(client):
    response = client.post(
        "/schedules",
        json={
            "weekday": 0,
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 401


def test_list_schedules_without_auth(client):
    response = client.get("/schedules")

    assert response.status_code == 401
