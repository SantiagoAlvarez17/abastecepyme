"""
Acceptance tests — Feature 4: Supply dashboard (dashboard section).

Consumes the real REST API (it does not import backend code). It reproduces the
client's demo on the dashboard: load a dependency, simulate an unavailability,
identify the consequences and then show a valid order or a clear cycle alert.

Requires the API running on an EMPTY database, for example:

    del aceptacion.db
    set DATABASE_URL=sqlite:///./aceptacion.db
    uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000

Usage:
    python scripts/aceptacion_f4.py [BASE_URL]   (default http://localhost:8000)

Test graph (A -> B reads "to produce A I need B"):

    Pan -> Masa madre -> Harina -> Molinos SA
    Torta -> Harina, Torta -> Huevos -> Granja El Roble        Panela (isolated)

The script ends by registering a cycle, so the database must be deleted before re-running it.
"""
import json
import sys
import urllib.error
import urllib.request
import uuid

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
results: list[bool] = []

ELEMENTS = [
    ("Molinos SA", "proveedor"),
    ("Granja El Roble", "proveedor"),
    ("Harina", "insumo"),
    ("Huevos", "insumo"),
    ("Panela", "insumo"),
    ("Masa madre", "producto"),
    ("Pan", "producto"),
    ("Torta", "producto"),
]
DEPENDENCIES = [
    ("Harina", "Molinos SA"),
    ("Huevos", "Granja El Roble"),
    ("Masa madre", "Harina"),
    ("Pan", "Masa madre"),
    ("Torta", "Huevos"),
]
# Loaded live during the demo (scenario "load a dependency").
DEMO_DEPENDENCY = ("Torta", "Harina")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE_URL + path, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")
    except TimeoutError:
        return 0, None  # the API did not answer: the scenario fails instead of hanging


def scenario(name, expected, obtained, passed):
    results.append(passed)
    print(f"[{'PASA ' if passed else 'FALLA'}] {name}")
    print(f"        esperado: {expected}")
    print(f"        obtenido: {obtained}\n")


def error_code(body):
    return body.get("error_code") if isinstance(body, dict) else None


def summary():
    return call("GET", "/dashboard/summary")


def register(ids, requiring, required):
    return call(
        "POST",
        "/dependencies",
        {"requiring_element_id": ids[requiring], "required_element_id": ids[required]},
    )


def prepare_catalog():
    ids = {}
    for name, element_type in ELEMENTS:
        st, body = call("POST", "/elements", {"name": name, "element_type": element_type})
        if st != 201:
            return ids, False
        ids[name] = body["id"]
    for requiring, required in DEPENDENCIES:
        st, _ = register(ids, requiring, required)
        if st != 201:
            return ids, False
    return ids, True


def empty_catalog_scenario():
    st, body = summary()
    production = (body or {}).get("production", {})
    scenario("Consulta sin datos: tablero de un catálogo vacío",
             "200, 0 elementos, estado 'empty' y sin puntos críticos",
             f"{st}, {body.get('total_elements')} elementos, estado={production.get('status')}, "
             f"críticos={body.get('critical_points')}",
             st == 200 and body["total_elements"] == 0 and production.get("status") == "empty"
             and body["critical_points"] == [])


def valid_chain_scenarios(ids):
    st, body = register(ids, *DEMO_DEPENDENCY)
    scenario("Demo 1/3 — Cargar una dependencia",
             "201 al registrar 'Para producir Torta necesito Harina'",
             st, st == 201)

    st, body = summary()
    production = body["production"]
    scenario("Cadena válida: el tablero integra catálogo y orden",
             "200, 8 elementos, 6 dependencias, aislado=[Panela], orden válido en 4 etapas",
             f"{st}, {body['total_elements']} elementos, {body['total_dependencies']} dependencias, "
             f"aislados={[e['name'] for e in body['isolated']]}, "
             f"estado={production['status']}, etapas={production['stage_count']}",
             st == 200 and body["total_elements"] == 8 and body["total_dependencies"] == 6
             and [e["name"] for e in body["isolated"]] == ["Panela"]
             and production["status"] == "valid" and production["stage_count"] == 4)

    ranking = [(p["name"], p["affected_products"]) for p in body["critical_points"]]
    scenario("Cadena válida: puntos críticos ordenados por productos detenidos",
             "Molinos SA (3) primero, luego Harina (3); ningún producto ni Panela en el ranking",
             ranking,
             ranking[:2] == [("Molinos SA", 3), ("Harina", 3)]
             and "Panela" not in [name for name, _ in ranking]
             and all(p["element_type"] != "producto" for p in body["critical_points"]))

    st, impact = call("GET", f"/impact/{ids['Molinos SA']}?mode=impact")
    affected = sorted(e["name"] for level in impact.get("levels", []) for e in level["elements"])
    scenario("Demo 2/3 — Simular indisponibilidad de Molinos SA e identificar consecuencias",
             "200, cadena con Harina, Masa madre, Pan y Torta afectados",
             f"{st}, resultado={impact.get('outcome')}, afectados={affected}",
             st == 200 and impact["outcome"] == "chain"
             and affected == ["Harina", "Masa madre", "Pan", "Torta"])

    st, order = call("GET", "/production-order")
    names = [step["name"] for step in order.get("steps", [])] if st == 200 else []
    position = {name: i for i, name in enumerate(names)}
    each_after_requirements = all(
        position[requiring] > position[required]
        for requiring, required in [*DEPENDENCIES, DEMO_DEPENDENCY]
    ) if len(names) == 8 else False
    scenario("Demo 3/3 — Mostrar un orden válido",
             "200, 8 pasos y cada elemento después de lo que necesita",
             f"{st}, pasos={names}",
             st == 200 and each_after_requirements)


def nonexistent_element_scenario():
    missing = str(uuid.uuid4())
    st, body = call("GET", f"/impact/{missing}?mode=impact")
    scenario("Elemento inexistente: simular la indisponibilidad de un ID que no existe",
             "404 ERR_ELEMENT_NOT_FOUND",
             f"{st} {error_code(body)}",
             st == 404 and error_code(body) == "ERR_ELEMENT_NOT_FOUND")


def invalid_data_scenarios(ids):
    for limit in ("0", "51", "abc"):
        st, body = call("GET", f"/dashboard/summary?limit={limit}")
        scenario(f"Dato inválido: límite de puntos críticos = {limit!r}",
                 "422 ERR_VALIDATION",
                 f"{st} {error_code(body)}",
                 st == 422 and error_code(body) == "ERR_VALIDATION")

    st, body = call("GET", "/impact/no-es-un-uuid?mode=impact")
    scenario("Dato inválido: simular indisponibilidad con un ID mal formado",
             "422 ERR_VALIDATION",
             f"{st} {error_code(body)}",
             st == 422 and error_code(body) == "ERR_VALIDATION")

    st, body = call("POST", "/dependencies",
                    {"requiring_element_id": ids["Pan"], "required_element_id": "123"})
    scenario("Dato inválido: cargar una dependencia con formato incorrecto",
             "422 ERR_VALIDATION",
             f"{st} {error_code(body)}",
             st == 422 and error_code(body) == "ERR_VALIDATION")


def cycle_scenarios(ids):
    st, _ = register(ids, "Masa madre", "Pan")
    scenario("Ciclo: cargar 'Para producir Masa madre necesito Pan'",
             "201 (F1 registra ciclos largos; detectarlos es de F3/F4)",
             st, st == 201)

    st, body = summary()
    production = body["production"]
    cycles = [c["text"] for c in production["cycles"]]
    scenario("Ciclo: el tablero muestra una alerta clara sin dejar de funcionar",
             "200, estado 'cycle', ciclo exacto 'Masa madre → Pan → Masa madre', sin etapas",
             f"{st}, estado={production['status']}, ciclos={cycles}, etapas={production['stage_count']}",
             st == 200 and production["status"] == "cycle"
             and cycles == ["Masa madre → Pan → Masa madre"] and production["stage_count"] == 0
             and "Ciclo detectado" in production["message"])

    st, body = call("GET", "/production-order")
    scenario("Ciclo: el orden de producción no inventa una secuencia",
             "409 ERR_CYCLE_DETECTED y sin 'steps'",
             f"{st} {error_code(body)}, steps={'steps' in (body or {})}",
             st == 409 and error_code(body) == "ERR_CYCLE_DETECTED" and "steps" not in body)


def main():
    try:
        st, graph = call("GET", "/graph")
    except urllib.error.URLError:
        print(f"No se pudo conectar con la API en {BASE_URL}. ¿Está corriendo uvicorn?")
        sys.exit(2)
    if graph["nodes"]:
        print("La base no está vacía: reinicie la API con una base nueva y vuelva a ejecutar.")
        sys.exit(1)

    empty_catalog_scenario()

    ids, ready = prepare_catalog()
    if not ready:
        print("No se pudo preparar el escenario; no tiene sentido seguir.")
        sys.exit(1)

    valid_chain_scenarios(ids)
    nonexistent_element_scenario()
    invalid_data_scenarios(ids)
    cycle_scenarios(ids)

    total, passed = len(results), sum(results)
    print(f"Resultado: {passed}/{total} escenarios pasaron")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
