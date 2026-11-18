"""
Pruebas de integración del reporte de ciclos en GET /production-order (Feature 3),
con SQLite en memoria. Usan el fixture `client` de conftest.py.
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


def test_ciclo_reporta_el_camino_exacto_y_separa_a_quienes_solo_dependen_de_el(client):
    molino = crear_elemento(client, "Molinos SA", "proveedor")
    harina = crear_elemento(client, "Harina", "insumo")
    masa = crear_elemento(client, "Masa madre", "producto")
    pan = crear_elemento(client, "Pan", "producto")
    croissant = crear_elemento(client, "Croissant", "producto")
    combo = crear_elemento(client, "Combo desayuno", "producto")
    registrar_dependencia(client, harina, molino)
    registrar_dependencia(client, masa, harina)
    registrar_dependencia(client, masa, pan)
    registrar_dependencia(client, pan, masa)  # ciclo Masa madre <-> Pan
    registrar_dependencia(client, croissant, masa)  # solo depende del ciclo
    registrar_dependencia(client, combo, croissant)  # solo depende del ciclo

    respuesta = client.get("/production-order")

    assert respuesta.status_code == 409
    cuerpo = respuesta.json()
    assert cuerpo["error_code"] == "ERR_CYCLE_DETECTED"
    assert "steps" not in cuerpo  # nunca se presenta un orden falso

    assert len(cuerpo["cycles"]) == 1
    ciclo = cuerpo["cycles"][0]
    assert ciclo["text"] == "Masa madre → Pan → Masa madre"
    assert [e["name"] for e in ciclo["elements"]] == ["Masa madre", "Pan", "Masa madre"]
    assert ciclo["elements"][0]["id"] == masa["id"] and ciclo["elements"][1]["id"] == pan["id"]
    assert ciclo["elements"][0]["element_type"] == "producto"

    assert [e["name"] for e in cuerpo["blocked_by_cycle"]] == ["Combo desayuno", "Croissant"]
    assert croissant["id"] in [e["id"] for e in cuerpo["blocked_by_cycle"]]

    # El mensaje nombra el ciclo y, aparte, a quienes solo dependen de él; no acusa a lo ajeno.
    assert cuerpo["message"].startswith("Ciclo detectado: Masa madre → Pan → Masa madre.")
    assert "dependen del ciclo: Combo desayuno, Croissant" in cuerpo["message"]
    assert "Molinos SA" not in cuerpo["message"] and "Harina" not in cuerpo["message"]


def test_ciclo_largo_se_muestra_en_el_sentido_de_las_dependencias(client):
    pastel = crear_elemento(client, "Pastel", "producto")
    relleno = crear_elemento(client, "Relleno", "producto")
    crema = crear_elemento(client, "Crema", "producto")
    registrar_dependencia(client, pastel, relleno)  # Pastel necesita Relleno
    registrar_dependencia(client, relleno, crema)  # Relleno necesita Crema
    registrar_dependencia(client, crema, pastel)  # Crema necesita Pastel

    cuerpo = client.get("/production-order").json()

    assert [c["text"] for c in cuerpo["cycles"]] == ["Crema → Pastel → Relleno → Crema"]
    assert cuerpo["blocked_by_cycle"] == []
    assert "dependen del ciclo" not in cuerpo["message"]


def test_varios_ciclos_se_numeran_en_el_mensaje(client):
    a = crear_elemento(client, "A", "producto")
    b = crear_elemento(client, "B", "producto")
    c = crear_elemento(client, "C", "producto")
    d = crear_elemento(client, "D", "producto")
    for requiere, requerido in [(a, b), (b, a), (c, d), (d, c)]:
        registrar_dependencia(client, requiere, requerido)

    cuerpo = client.get("/production-order").json()

    assert [x["text"] for x in cuerpo["cycles"]] == ["A → B → A", "C → D → C"]
    assert cuerpo["message"].startswith("Ciclos detectados (2):")
    assert "1) A → B → A." in cuerpo["message"] and "2) C → D → C." in cuerpo["message"]


def test_sin_ciclo_la_respuesta_es_un_orden_y_no_trae_campos_de_ciclo(client):
    molino = crear_elemento(client, "Molinos SA", "proveedor")
    harina = crear_elemento(client, "Harina", "insumo")
    registrar_dependencia(client, harina, molino)

    respuesta = client.get("/production-order")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert "cycles" not in cuerpo and "blocked_by_cycle" not in cuerpo
    assert [paso["name"] for paso in cuerpo["steps"]] == ["Molinos SA", "Harina"]
