"""
Pruebas de aceptación — Feature 3: Orden de preparación.

Consume la API REST real (no importa el código del backend).
Requiere la API corriendo sobre una base VACÍA, por ejemplo:

    del aceptacion.db
    set DATABASE_URL=sqlite:///./aceptacion.db
    uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000

Uso:
    python scripts/aceptacion_f3.py [URL_BASE]   (por defecto http://localhost:8000)

Grafo de prueba (A -> B se lee "para producir A necesito B"):

    Pan -> Masa madre -> Harina   -> Molinos SA
                      -> Levadura -> Molinos SA
    Torta -> Harina, Huevos -> Granja El Roble        Panela (sin dependencias)

El script termina registrando un ciclo, así que la base queda "contradictoria":
bórrela antes de volver a ejecutarlo.
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")
    except TimeoutError:
        return 0, None  # la API no respondió: el escenario falla en lugar de colgarse


def escenario(nombre, esperado, obtenido, paso):
    resultados.append(paso)
    print(f"[{'PASA ' if paso else 'FALLA'}] {nombre}")
    print(f"        esperado: {esperado}")
    print(f"        obtenido: {obtenido}\n")


def codigo_error(cuerpo):
    return cuerpo.get("error_code") if isinstance(cuerpo, dict) else None


def etapas(orden):
    """Lista de conjuntos de nombres, uno por etapa, en orden."""
    resultado = []
    for paso in orden["steps"]:
        while len(resultado) < paso["stage"]:
            resultado.append(set())
        resultado[paso["stage"] - 1].add(paso["name"])
    return resultado


def preparar_catalogo():
    """Crea los elementos y dependencias del escenario. Devuelve (ids, ok)."""
    ids = {}
    elementos = [("Molinos SA", "proveedor"), ("Granja El Roble", "proveedor"),
                 ("Harina", "insumo"), ("Levadura", "insumo"), ("Huevos", "insumo"),
                 ("Masa madre", "producto"), ("Pan", "producto"), ("Torta", "producto"),
                 ("Panela", "producto")]
    for nombre, tipo in elementos:
        st, cuerpo = llamar("POST", "/elements", {"name": nombre, "element_type": tipo})
        ids[nombre] = cuerpo.get("id") if st == 201 else None
    aristas = [("Harina", "Molinos SA"), ("Levadura", "Molinos SA"), ("Huevos", "Granja El Roble"),
               ("Masa madre", "Harina"), ("Masa madre", "Levadura"), ("Pan", "Masa madre"),
               ("Torta", "Harina"), ("Torta", "Huevos")]
    estados = [llamar("POST", "/dependencies",
                      {"requiring_element_id": ids[a], "required_element_id": ids[b]})[0]
               for a, b in aristas]
    ok = all(ids.values()) and all(s == 201 for s in estados)
    escenario("Preparación: 9 elementos y 8 dependencias",
              "todos creados con 201",
              f"{sum(1 for v in ids.values() if v)} elementos, {estados.count(201)} dependencias", ok)
    return ids, ok


def escenarios_sin_ciclos(ids):
    """Caso acíclico: hay un orden de preparación válido."""
    st, orden = llamar("GET", "/production-order")
    pasos = orden["steps"] if st == 200 else []
    escenario("Normal: se genera el orden de preparación de todo el catálogo",
              "200, 9 elementos en 4 etapas: {Granja El Roble, Molinos SA, Panela} → {Harina, Huevos, Levadura} → {Masa madre, Torta} → {Pan}",
              f"{st}, {orden.get('total_elements')} elementos en {orden.get('stage_count')} etapas: {etapas(orden) if st == 200 else None}",
              st == 200 and orden["total_elements"] == 9 and orden["stage_count"] == 4
              and etapas(orden) == [{"Granja El Roble", "Molinos SA", "Panela"},
                                    {"Harina", "Huevos", "Levadura"},
                                    {"Masa madre", "Torta"},
                                    {"Pan"}])

    posicion = {p["name"]: p["position"] for p in pasos}
    violaciones = [(p["name"], r) for p in pasos for r in p["requires"] if posicion[r] >= p["position"]]
    escenario("Normal: cada elemento aparece después de todo lo que necesita",
              "ninguna violación (todo requisito tiene una posición menor)",
              f"{len(violaciones)} violaciones {violaciones}",
              len(pasos) == 9 and not violaciones)

    escenario("Normal: posiciones consecutivas y sin elementos repetidos",
              "posiciones 1..9 y 9 nombres distintos",
              f"posiciones={[p['position'] for p in pasos]}, distintos={len({p['name'] for p in pasos})}",
              [p["position"] for p in pasos] == list(range(1, 10)) and len({p["name"] for p in pasos}) == 9)

    paso_pan = next((p for p in pasos if p["name"] == "Pan"), None)
    escenario("Normal: cada paso informa sus requisitos directos",
              "Pan requiere solo Masa madre",
              f"Pan requiere {paso_pan and paso_pan['requires']}",
              paso_pan is not None and paso_pan["requires"] == ["Masa madre"])

    st2, orden2 = llamar("GET", "/production-order")
    escenario("Estabilidad: dos consultas seguidas devuelven exactamente el mismo orden",
              "órdenes idénticos",
              "idénticos" if orden2 == orden else "distintos",
              st2 == 200 and orden2 == orden)

    panela = next((p for p in pasos if p["name"] == "Panela"), None)
    escenario("Sin dependencias: Panela no espera a nadie",
              "etapa 1 (puede prepararse desde el inicio)",
              f"etapa {panela and panela['stage']}",
              panela is not None and panela["stage"] == 1)

    st, cuerpo = llamar("POST", "/dependencies",
                        {"requiring_element_id": ids["Torta"], "required_element_id": ids["Pan"]})
    st_orden, nuevo = llamar("GET", "/production-order")
    etapa_torta = next((p["stage"] for p in nuevo.get("steps", []) if p["name"] == "Torta"), None) if st_orden == 200 else None
    escenario("Cambio de dependencias: si Torta ahora necesita Pan, el orden se recalcula",
              "dependencia registrada (201); Torta pasa a la etapa 5 y el orden sigue siendo válido",
              f"registro {st}, Torta en etapa {etapa_torta}, {nuevo.get('stage_count')} etapas",
              st == 201 and st_orden == 200 and etapa_torta == 5 and nuevo["stage_count"] == 5)


def escenarios_con_ciclo(ids):
    """Caso cíclico: las dependencias se contradicen y no debe presentarse ningún orden."""
    st, _ = llamar("POST", "/dependencies",
                   {"requiring_element_id": ids["Pan"], "required_element_id": ids["Torta"]})
    escenario("Ciclo: se registra 'Pan necesita Torta' (Torta ya necesitaba Pan)",
              "201 (el catálogo guarda la relación; el orden es quien detecta la contradicción)", st, st == 201)

    st, cuerpo = llamar("GET", "/production-order")
    mensaje = (cuerpo or {}).get("message", "")
    escenario("Ciclo: no se presenta un orden falso",
              "409 ERR_CYCLE_DETECTED, sin la lista de pasos",
              f"{st} {codigo_error(cuerpo)}, 'steps' presente: {isinstance(cuerpo, dict) and 'steps' in cuerpo}",
              st == 409 and codigo_error(cuerpo) == "ERR_CYCLE_DETECTED" and "steps" not in cuerpo)

    escenario("Ciclo: el mensaje señala a los elementos bloqueados y no a los demás",
              "menciona Pan y Torta; no menciona Molinos SA ni Panela",
              mensaje,
              "Pan" in mensaje and "Torta" in mensaje and "Molinos SA" not in mensaje and "Panela" not in mensaje)


def main():
    try:
        llamar("GET", "/graph")
    except urllib.error.URLError:
        print(f"No se pudo conectar con la API en {BASE_URL}. ¿Está corriendo uvicorn?")
        sys.exit(2)

    st, grafo = llamar("GET", "/graph")
    if grafo["nodes"]:
        print("La base no está vacía: reinicie la API con una base nueva y vuelva a ejecutar.")
        sys.exit(1)

    # --- Consulta sin datos (catálogo vacío) ---
    st, orden = llamar("GET", "/production-order")
    escenario("Consulta sin datos: el orden de un catálogo vacío",
              "200, sin pasos y 0 elementos",
              f"{st}, {orden.get('total_elements')} elementos, pasos={orden.get('steps')}",
              st == 200 and orden["steps"] == [] and orden["total_elements"] == 0)

    ids, listo = preparar_catalogo()
    if not listo:
        print("No se pudo preparar el escenario; no tiene sentido seguir.")
        sys.exit(1)

    escenarios_sin_ciclos(ids)
    escenarios_con_ciclo(ids)

    total, ok = len(resultados), sum(resultados)
    print(f"Resultado: {ok}/{total} escenarios pasaron")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()