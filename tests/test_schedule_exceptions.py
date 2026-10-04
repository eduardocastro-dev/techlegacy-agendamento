def test_create_closed_schedule_exception(client):
    response = client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-09-28",
            "closed": True,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["establishment_id"] == 1
    assert data["date"] == "2026-09-28"
    assert data["closed"] is True
    assert data["opening_time"] is None
    assert data["closing_time"] is None


def test_create_schedule_exception_with_custom_hours(client):
    response = client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-09-29",
            "opening_time": "10:00",
            "closing_time": "15:00",
            "closed": False,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["opening_time"] == "10:00"
    assert data["closing_time"] == "15:00"
    assert data["closed"] is False


def test_create_schedule_exception_invalid_date(client):
    response = client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "28/09/2026",
            "closed": True,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"


def test_create_schedule_exception_invalid_hours(client):
    response = client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-09-30",
            "opening_time": "18:00",
            "closing_time": "08:00",
            "closed": False,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"


def test_create_duplicate_schedule_exception(client):
    payload = {
        "establishment_id": 1,
        "date": "2026-10-01",
        "closed": True,
    }

    first = client.post(
        "/schedule-exceptions",
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/schedule-exceptions",
        json=payload,
    )

    assert second.status_code == 409


def test_list_schedule_exceptions(client):
    client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-10-02",
            "closed": True,
        },
    )

    client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-10-01",
            "closed": True,
        },
    )

    response = client.get(
        "/schedule-exceptions?establishment_id=1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["date"] == "2026-10-01"
    assert data[1]["date"] == "2026-10-02"


def test_get_schedule_exception(client):
    create_response = client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-10-03",
            "closed": True,
        },
    )

    exception_id = create_response.get_json()["id"]

    response = client.get(
        f"/schedule-exceptions/{exception_id}"
        "?establishment_id=1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == exception_id


def test_update_schedule_exception(client):
    create_response = client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-10-04",
            "closed": True,
        },
    )

    exception_id = create_response.get_json()["id"]

    response = client.put(
        f"/schedule-exceptions/{exception_id}"
        "?establishment_id=1",
        json={
            "opening_time": "09:00",
            "closing_time": "17:00",
            "closed": False,
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["opening_time"] == "09:00"
    assert data["closing_time"] == "17:00"
    assert data["closed"] is False


def test_delete_schedule_exception(client):
    create_response = client.post(
        "/schedule-exceptions",
        json={
            "establishment_id": 1,
            "date": "2026-10-05",
            "closed": True,
        },
    )

    exception_id = create_response.get_json()["id"]

    response = client.delete(
        f"/schedule-exceptions/{exception_id}"
        "?establishment_id=1"
    )

    assert response.status_code == 200

    response = client.get(
        f"/schedule-exceptions/{exception_id}"
        "?establishment_id=1"
    )

    assert response.status_code == 404