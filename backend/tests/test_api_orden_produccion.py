"""
Pruebas de integración de GET /production-order (Feature 3), con SQLite en memoria.
Usan el fixture `client` de conftest.py.
"""


def crear_elemento(client, nombre, tipo):
    respuesta = client.post("/elements", json={"name": nombre, "element_type": tipo})
    assert respuesta.status_code == 201
    return respuesta.json()


def registrar_dependencia(client, requiere, requerido):
    return client.post(
        "/dependencies",
        json={"requiring_element_id": requiere["id"], "required_element_id": requerido["id"]},
    )


def test_orden_con_catalogo_vacio_es_valido_y_no_tiene_pasos(client):
    respuesta = client.get("/production-order")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["steps"] == []
    assert cuerpo["total_elements"] == 0
    assert cuerpo["stage_count"] == 0
    assert "vacío" in cuerpo["summary"]


def test_orden_valido_pone_cada_requisito_antes_de_quien_lo_necesita(client):
    molino = crear_elemento(client, "Molinos SA", "proveedor")
    harina = crear_elemento(client, "Harina", "insumo")
    masa = crear_elemento(client, "Masa madre", "producto")
    pan = crear_elemento(client, "Pan", "producto")
    registrar_dependencia(client, harina, molino)
    registrar_dependencia(client, masa, harina)
    registrar_dependencia(client, pan, masa)

    respuesta = client.get("/production-order")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert [paso["name"] for paso in cuerpo["steps"]] == ["Molinos SA", "Harina", "Masa madre", "Pan"]
    assert [paso["position"] for paso in cuerpo["steps"]] == [1, 2, 3, 4]
    assert [paso["stage"] for paso in cuerpo["steps"]] == [1, 2, 3, 4]
    assert cuerpo["total_elements"] == 4
    assert cuerpo["stage_count"] == 4

    posicion = {paso["name"]: paso["position"] for paso in cuerpo["steps"]}
    for paso in cuerpo["steps"]:
        assert all(posicion[requisito] < paso["position"] for requisito in paso["requires"])
    assert cuerpo["steps"][3]["requires"] == ["Masa madre"]


def test_orden_agrupa_en_una_etapa_a_los_elementos_independientes(client):
    molino = crear_elemento(client, "Molinos SA", "proveedor")
    granja = crear_elemento(client, "Granja El Roble", "proveedor")
    harina = crear_elemento(client, "Harina", "insumo")
    huevos = crear_elemento(client, "Huevos", "insumo")
    panela = crear_elemento(client, "Panela", "producto")  # aislado
    registrar_dependencia(client, harina, molino)
    registrar_dependencia(client, huevos, granja)

    cuerpo = client.get("/production-order").json()

    etapa_1 = [paso["name"] for paso in cuerpo["steps"] if paso["stage"] == 1]
    etapa_2 = [paso["name"] for paso in cuerpo["steps"] if paso["stage"] == 2]
    assert etapa_1 == ["Granja El Roble", "Molinos SA", "Panela"]
    assert etapa_2 == ["Harina", "Huevos"]
    assert cuerpo["stage_count"] == 2
    assert panela["name"] in etapa_1


def test_orden_se_recalcula_cuando_cambian_las_dependencias(client):
    molino = crear_elemento(client, "Molinos SA", "proveedor")
    harina = crear_elemento(client, "Harina", "insumo")
    masa = crear_elemento(client, "Masa madre", "producto")
    torta = crear_elemento(client, "Torta", "producto")
    registrar_dependencia(client, harina, molino)
    registrar_dependencia(client, masa, harina)
    registrar_dependencia(client, torta, harina)

    antes = {p["name"]: p["stage"] for p in client.get("/production-order").json()["steps"]}
    assert antes["Torta"] == antes["Masa madre"] == 3

    registrar_dependencia(client, torta, masa)  # ahora la torta también necesita la masa madre

    despues = {p["name"]: p["stage"] for p in client.get("/production-order").json()["steps"]}
    assert despues["Torta"] == 4


def test_orden_con_ciclo_responde_409_y_no_entrega_ningun_orden(client):
    molino = crear_elemento(client, "Molinos SA", "proveedor")
    harina = crear_elemento(client, "Harina", "insumo")
    masa = crear_elemento(client, "Masa madre", "producto")
    pan = crear_elemento(client, "Pan", "producto")
    registrar_dependencia(client, harina, molino)
    registrar_dependencia(client, masa, harina)
    registrar_dependencia(client, masa, pan)
    registrar_dependencia(client, pan, masa)  # cierra el ciclo Masa madre <-> Pan

    respuesta = client.get("/production-order")

    assert respuesta.status_code == 409
    cuerpo = respuesta.json()
    assert cuerpo["error_code"] == "ERR_CYCLE_DETECTED"
    assert "steps" not in cuerpo  # nunca se presenta un orden falso
    assert cuerpo["message"] in (
        "Ciclo detectado: Masa madre → Pan → Masa madre. Las dependencias se contradicen, "
        "por lo que no existe un orden de preparación válido.",
        "Ciclo detectado: Pan → Masa madre → Pan. Las dependencias se contradicen, "
        "por lo que no existe un orden de preparación válido.",
    )
    assert "Molinos SA" not in cuerpo["message"]  # lo que no depende del ciclo no se acusa