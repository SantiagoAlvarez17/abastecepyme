"""
Pruebas de aceptación — Feature 1: Catálogo de dependencias.

Consume la API REST real (no importa el código del backend).
Requiere la API corriendo sobre una base VACÍA, por ejemplo:

    del aceptacion.db
    set DATABASE_URL=sqlite:///./aceptacion.db
    uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000

Uso:
    python scripts/aceptacion_f1.py [URL_BASE]   (por defecto http://localhost:8000)
"""
import json
import sys
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
resultados = []


def llamar(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(
        BASE_URL + ruta, data=datos, method=metodo,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")


def escenario(nombre, esperado, obtenido, paso):
    resultados.append(paso)
    print(f"[{'PASA ' if paso else 'FALLA'}] {nombre}")
    print(f"        esperado: {esperado}")
    print(f"        obtenido: {obtenido}\n")


def codigo_error(cuerpo):
    return cuerpo.get("error_code") if isinstance(cuerpo, dict) else None


def main():
    try:
        llamar("GET", "/graph")
    except urllib.error.URLError:
        print(f"No se pudo conectar con la API en {BASE_URL}. ¿Está corriendo uvicorn?")
        sys.exit(2)

    # --- Grafo vacío ---
    st, g = llamar("GET", "/graph")
    escenario("Grafo vacío: GET /graph sin datos",
              "200, 0 nodos y 0 aristas",
              f"{st}, {len(g['nodes'])} nodos y {len(g['edges'])} aristas",
              st == 200 and g["nodes"] == [] and g["edges"] == [])
    if g["nodes"]:
        print("La base no está vacía: reinicie la API con una base nueva y vuelva a ejecutar.")
        sys.exit(1)

    # --- Escenario normal de negocio ---
    creados = {}
    for nombre, tipo in [("Molinos SA", "proveedor"), ("Harina", "insumo"),
                         ("Levadura", "insumo"), ("Masa madre", "producto"), ("Pan", "producto")]:
        st, cuerpo = llamar("POST", "/elements", {"name": nombre, "element_type": tipo})
        creados[nombre] = cuerpo.get("id") if st == 201 else None
        escenario(f"Normal: crear {tipo} '{nombre}'", "201 con id",
                  f"{st}, id={creados[nombre]}", st == 201 and creados[nombre] is not None)

    st, lista = llamar("GET", "/elements")
    escenario("Normal: listar elementos", "200 con 5 elementos",
              f"{st} con {len(lista)} elementos", st == 200 and len(lista) == 5)

    aristas = [("Harina", "Molinos SA"), ("Levadura", "Molinos SA"),
               ("Masa madre", "Harina"), ("Masa madre", "Levadura"), ("Pan", "Masa madre")]
    for a, b in aristas:
        st, cuerpo = llamar("POST", "/dependencies",
                            {"requiring_element_id": creados[a], "required_element_id": creados[b]})
        escenario(f"Normal: 'Para producir {a} necesito {b}'", "201", st, st == 201)

    st, g = llamar("GET", "/graph")
    ady_pan = g["adjacency"].get(creados["Pan"], [])
    escenario("Normal: GET /graph muestra la red",
              "200, 5 nodos, 5 aristas, Pan -> [Masa madre]",
              f"{st}, {len(g['nodes'])} nodos, {len(g['edges'])} aristas, Pan -> {ady_pan}",
              st == 200 and len(g["nodes"]) == 5 and len(g["edges"]) == 5
              and ady_pan == [creados["Masa madre"]])

    st, deps = llamar("GET", "/dependencies")
    escenario("Normal: GET /dependencies", "200 con 5 aristas",
              f"{st} con {len(deps)} aristas", st == 200 and len(deps) == 5)

    # --- Nodo inexistente ---
    fantasma = "00000000-0000-0000-0000-000000000000"
    st, cuerpo = llamar("POST", "/dependencies",
                        {"requiring_element_id": creados["Pan"], "required_element_id": fantasma})
    escenario("Nodo inexistente: Pan requiere un id que no existe",
              "404 ERR_ELEMENT_NOT_FOUND", f"{st} {codigo_error(cuerpo)}",
              st == 404 and codigo_error(cuerpo) == "ERR_ELEMENT_NOT_FOUND")

    # --- Relación repetida ---
    st, cuerpo = llamar("POST", "/dependencies",
                        {"requiring_element_id": creados["Pan"], "required_element_id": creados["Masa madre"]})
    escenario("Relación repetida: Pan requiere Masa madre otra vez",
              "409 ERR_DUPLICATE_DEPENDENCY", f"{st} {codigo_error(cuerpo)}",
              st == 409 and codigo_error(cuerpo) == "ERR_DUPLICATE_DEPENDENCY")

    # --- Autodependencia ---
    st, cuerpo = llamar("POST", "/dependencies",
                        {"requiring_element_id": creados["Pan"], "required_element_id": creados["Pan"]})
    escenario("Autodependencia: Pan requiere Pan",
              "400 ERR_SELF_DEPENDENCY", f"{st} {codigo_error(cuerpo)}",
              st == 400 and codigo_error(cuerpo) == "ERR_SELF_DEPENDENCY")

    # --- Identificador repetido (nombre, sin distinguir mayúsculas ni espacios) ---
    st, cuerpo = llamar("POST", "/elements", {"name": "  harina ", "element_type": "insumo"})
    escenario("Identificador repetido: crear '  harina ' cuando existe 'Harina'",
              "409 ERR_DUPLICATE_ELEMENT", f"{st} {codigo_error(cuerpo)}",
              st == 409 and codigo_error(cuerpo) == "ERR_DUPLICATE_ELEMENT")

    # --- Datos inválidos ---
    casos_invalidos = [
        ("nombre vacío", "/elements", {"name": "   ", "element_type": "insumo"}),
        ("tipo inexistente", "/elements", {"name": "Azúcar", "element_type": "maquina"}),
        ("falta el tipo", "/elements", {"name": "Azúcar"}),
        ("id mal formado", "/dependencies", {"requiring_element_id": "abc", "required_element_id": creados["Pan"]}),
    ]
    for nombre, ruta, cuerpo_req in casos_invalidos:
        st, cuerpo = llamar("POST", ruta, cuerpo_req)
        escenario(f"Dato inválido: {nombre}", "422 ERR_VALIDATION con message",
                  f"{st} {codigo_error(cuerpo)}",
                  st == 422 and codigo_error(cuerpo) == "ERR_VALIDATION" and "message" in cuerpo)

    # --- Relación sin sentido de negocio ---
    st, cuerpo = llamar("POST", "/dependencies",
                        {"requiring_element_id": creados["Molinos SA"], "required_element_id": creados["Harina"]})
    escenario("Relación inválida: 'Para producir Molinos SA necesito Harina'",
              "400 ERR_INVALID_DEPENDENCY_TYPE", f"{st} {codigo_error(cuerpo)}",
              st == 400 and codigo_error(cuerpo) == "ERR_INVALID_DEPENDENCY_TYPE")

    # --- Ciclo: F1 lo registra; la detección y alerta corresponde a F3 ---
    st, cuerpo = llamar("POST", "/dependencies",
                        {"requiring_element_id": creados["Masa madre"], "required_element_id": creados["Pan"]})
    escenario("Ciclo: Masa madre requiere Pan (y Pan requiere Masa madre)",
              "201 (el catálogo lo guarda; F3 lo detecta y alerta)", st, st == 201)

    # --- Resumen ---
    total, ok = len(resultados), sum(resultados)
    print(f"Resultado: {ok}/{total} escenarios pasaron")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
