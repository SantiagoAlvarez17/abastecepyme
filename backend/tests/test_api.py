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


def test_impacto_api_distingue_inexistente_aislado_sin_alcance_y_cadena(client):
    molino = crear_elemento(client, "Molinos SA", "proveedor")
    harina = crear_elemento(client, "Harina", "insumo")
    masa = crear_elemento(client, "Masa madre", "producto")
    pan = crear_elemento(client, "Pan", "producto")
    panela = crear_elemento(client, "Panela", "producto")

    registrar_dependencia(client, harina["id"], molino["id"])
    registrar_dependencia(client, masa["id"], harina["id"])
    registrar_dependencia(client, pan["id"], masa["id"])

    # 1. Elemento inexistente -> 404 ERR_ELEMENT_NOT_FOUND
    inexistente = client.get("/impact/00000000-0000-0000-0000-000000000000")
    assert inexistente.status_code == 404
    assert inexistente.json()["error_code"] == "ERR_ELEMENT_NOT_FOUND"

    # 2. Elemento aislado (sin ninguna dependencia) -> 200 isolated
    aislado = client.get(f"/impact/{panela['id']}").json()
    assert aislado["outcome"] == "isolated"
    assert aislado["affected_count"] == 0
    assert aislado["levels"] == []

    # 3. Elemento sin alcance en la dirección consultada -> 200 no_reach
    sin_alcance = client.get(f"/impact/{pan['id']}").json()
    assert sin_alcance["outcome"] == "no_reach"
    assert sin_alcance["affected_count"] == 0

    # 4. Impacto desde proveedor (recorrido inverso por niveles) -> 200 chain
    cadena_impacto = client.get(f"/impact/{molino['id']}").json()
    assert cadena_impacto["outcome"] == "chain"
    assert cadena_impacto["affected_count"] == 3
    assert cadena_impacto["max_level"] == 3
    assert [n["elements"][0]["name"] for n in cadena_impacto["levels"]] == [
        "Harina",
        "Masa madre",
        "Pan",
    ]
    assert cadena_impacto["levels"][2]["elements"][0]["path"] == [
        "Molinos SA",
        "Harina",
        "Masa madre",
        "Pan",
    ]

    # 5. Requisitos desde un producto (mode=requirements) -> 200 chain
    requisitos = client.get(f"/impact/{pan['id']}?mode=requirements").json()
    assert requisitos["outcome"] == "chain"
    assert requisitos["affected_count"] == 3
    assert [n["elements"][0]["name"] for n in requisitos["levels"]] == [
        "Masa madre",
        "Harina",
        "Molinos SA",
    ]
