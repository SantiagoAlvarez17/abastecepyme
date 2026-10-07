def crear_elemento(client, nombre, tipo):
    respuesta = client.post(
        "/elements",
        json={"name": nombre, "element_type": tipo},
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def registrar_dependencia(client, requiere, requerido):
    return client.post(
        "/dependencies",
        json={
            "requiring_element_id": requiere,
            "required_element_id": requerido,
        },
    )


def test_crear_y_listar_elementos(client):
    creado = crear_elemento(client, "Harina", "insumo")

    respuesta = client.get("/elements")

    assert respuesta.status_code == 200
    assert any(elemento["id"] == creado["id"] for elemento in respuesta.json())


def test_rechaza_nombre_vacio_y_tipo_invalido(client):
    nombre_vacio = client.post(
        "/elements",
        json={"name": "   ", "element_type": "insumo"},
    )
    tipo_invalido = client.post(
        "/elements",
        json={"name": "Azúcar", "element_type": "maquina"},
    )

    assert nombre_vacio.status_code == 422
    assert nombre_vacio.json()["error_code"] == "ERR_VALIDATION"
    assert tipo_invalido.status_code == 422
    assert tipo_invalido.json()["error_code"] == "ERR_VALIDATION"


def test_rechaza_uuid_mal_formado(client):
    respuesta = registrar_dependencia(client, "no-es-un-uuid", "tampoco")

    assert respuesta.status_code == 422
    assert respuesta.json()["error_code"] == "ERR_VALIDATION"


def test_rechaza_dependencia_duplicada_autodependencia_y_elemento_inexistente(client):
    harina = crear_elemento(client, "Harina", "insumo")
    molino = crear_elemento(client, "Molino", "proveedor")

    assert registrar_dependencia(
        client, harina["id"], molino["id"]
    ).status_code == 201

    duplicada = registrar_dependencia(client, harina["id"], molino["id"])
    propia = registrar_dependencia(client, harina["id"], harina["id"])
    inexistente = registrar_dependencia(
        client, harina["id"], "00000000-0000-0000-0000-000000000000"
    )

    assert duplicada.status_code == 409
    assert duplicada.json()["error_code"] == "ERR_DUPLICATE_DEPENDENCY"
    assert propia.status_code == 400
    assert propia.json()["error_code"] == "ERR_SELF_DEPENDENCY"
    assert inexistente.status_code == 404
    assert inexistente.json()["error_code"] == "ERR_ELEMENT_NOT_FOUND"


def test_acepta_y_rechaza_combinaciones_de_tipos(client):
    proveedor = crear_elemento(client, "Molino", "proveedor")
    insumo = crear_elemento(client, "Harina", "insumo")
    producto = crear_elemento(client, "Pan", "producto")
    producto_intermedio = crear_elemento(client, "Masa", "producto")

    assert registrar_dependencia(
        client, insumo["id"], proveedor["id"]
    ).status_code == 201
    assert registrar_dependencia(
        client, producto["id"], insumo["id"]
    ).status_code == 201
    assert registrar_dependencia(
        client, producto["id"], producto_intermedio["id"]
    ).status_code == 201

    casos_invalidos = [
        (proveedor["id"], insumo["id"]),
        (insumo["id"], producto["id"]),
        (producto["id"], proveedor["id"]),
    ]

    for requiere, requerido in casos_invalidos:
        respuesta = registrar_dependencia(client, requiere, requerido)
        assert respuesta.status_code == 400
        assert respuesta.json()["error_code"] == "ERR_INVALID_DEPENDENCY_TYPE"


def test_grafo_vacio(client):
    respuesta = client.get("/graph")

    assert respuesta.status_code == 200
    assert respuesta.json()["nodes"] == []
    assert respuesta.json()["edges"] == []
    assert respuesta.json()["adjacency"] == {}


def test_grafo_devuelve_aristas_y_adyacencia_coherentes(client):
    proveedor = crear_elemento(client, "Molino", "proveedor")
    insumo = crear_elemento(client, "Harina", "insumo")
    producto = crear_elemento(client, "Pan", "producto")

    registrar_dependencia(client, insumo["id"], proveedor["id"])
    registrar_dependencia(client, producto["id"], insumo["id"])

    grafo = client.get("/graph").json()
    aristas = {
        (arista["requiring_element_id"], arista["required_element_id"])
        for arista in grafo["edges"]
    }

    assert len(grafo["nodes"]) == 3
    assert aristas == {
        (insumo["id"], proveedor["id"]),
        (producto["id"], insumo["id"]),
    }
    assert grafo["adjacency"][producto["id"]] == [insumo["id"]]
    assert grafo["adjacency"][insumo["id"]] == [proveedor["id"]]