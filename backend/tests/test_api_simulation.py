def create_element(client, name, element_type):
    response = client.post(
        "/elements",
        json={"name": name, "element_type": element_type},
    )
    assert response.status_code == 201
    return response.json()


def create_dependency(client, requiring, required):
    return client.post(
        "/dependencies",
        json={
            "requiring_element_id": requiring["id"],
            "required_element_id": required["id"],
        },
    )


def test_simulacion_multifuente_identifica_productos_detenidos_y_disponibles(client):
    molino = create_element(client, "Molino", "proveedor")
    granja = create_element(client, "Granja", "proveedor")
    leche = create_element(client, "Leche", "insumo")
    harina = create_element(client, "Harina", "insumo")
    pan = create_element(client, "Pan", "producto")
    torta = create_element(client, "Torta", "producto")
    azucar = create_element(client, "Azúcar", "insumo")

    assert create_dependency(client, harina, molino).status_code == 201
    assert create_dependency(client, leche, granja).status_code == 201
    assert create_dependency(client, pan, harina).status_code == 201
    assert create_dependency(client, pan, leche).status_code == 201
    assert create_dependency(client, torta, azucar).status_code == 201

    response = client.post(
        "/simulations/unavailability",
        json={"element_ids": [molino["id"], granja["id"]]},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["affected_count"] == 3
    assert result["max_level"] == 2
    assert [[element["name"] for element in level["elements"]] for level in result["levels"]] == [
        ["Harina", "Leche"],
        ["Pan"],
    ]
    assert result["levels"][1]["elements"][0]["source_id"] == molino["id"]
    assert result["levels"][1]["elements"][0]["path"] == ["Molino", "Harina", "Pan"]
    assert [element["name"] for element in result["stopped_products"]] == ["Pan"]
    assert [element["name"] for element in result["available_products"]] == ["Torta"]


def test_simulacion_rechaza_lista_vacia(client):
    response = client.post("/simulations/unavailability", json={"element_ids": []})

    assert response.status_code == 422
    assert response.json()["error_code"] == "ERR_VALIDATION"


def test_simulacion_rechaza_identificadores_repetidos(client):
    element = create_element(client, "Molino", "proveedor")
    response = client.post(
        "/simulations/unavailability",
        json={"element_ids": [element["id"], element["id"]]},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "ERR_VALIDATION"


def test_simulacion_rechaza_uuid_mal_formado(client):
    response = client.post(
        "/simulations/unavailability",
        json={"element_ids": ["no-es-un-uuid"]},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "ERR_VALIDATION"


def test_simulacion_rechaza_identificador_inexistente(client):
    response = client.post(
        "/simulations/unavailability",
        json={"element_ids": ["00000000-0000-0000-0000-000000000000"]},
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "ERR_ELEMENT_NOT_FOUND"
