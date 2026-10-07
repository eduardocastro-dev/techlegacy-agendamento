def test_get_settings(client, auth_headers, establishment):

    response = client.get(
        "/settings",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == establishment
    assert data["name"] == "Estabelecimento Teste"
    assert data["slug"] == "estabelecimento-teste"
    assert data["phone"] == "11999999999"


def test_update_settings(
    client,
    auth_headers,
    establishment,
):

    response = client.put(
        "/settings",
        headers=auth_headers,
        json={
            "name": "Novo Nome",
            "phone": "11988887777",
            "slug": "novo-nome",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == establishment
    assert data["name"] == "Novo Nome"
    assert data["phone"] == "11988887777"
    assert data["slug"] == "novo-nome"
