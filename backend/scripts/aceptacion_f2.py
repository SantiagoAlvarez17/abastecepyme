"""
Pruebas de aceptación — Feature 2: Análisis de impacto.

Consume la API REST real (no importa el código del backend).
Requiere la API corriendo sobre una base VACÍA, por ejemplo:

    del aceptacion.db
    set DATABASE_URL=sqlite:///./aceptacion.db
    uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000

Uso:
    python scripts/aceptacion_f2.py [URL_BASE]   (por defecto http://localhost:8000)

Grafo de prueba (A -> B se lee "para producir A necesito B"):

    Pan -> Masa madre -> Harina   -> Molinos SA
                      -> Levadura -> Molinos SA
    Torta -> Harina, Huevos -> Granja El Roble        Panela (sin dependencias)
"""
import json
import sys
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
FANTASMA = "00000000-0000-0000-0000-000000000000"
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


def nombres(r):
    """Nombres de los elementos visitados, en orden de recorrido."""
    return [e["name"] for nivel in r["levels"] for e in nivel["elements"]]


def por_nivel(r):
    """Lista de conjuntos de nombres, uno por nivel."""
    return [{e["name"] for e in nivel["elements"]} for nivel in r["levels"]]


def impacto(ids, nombre, modo="impact"):
    return llamar("GET", f"/impact/{ids[nombre]}?mode={modo}")


def main():
    try:
        llamar("GET", "/graph")
    except urllib.error.URLError:
        print(f"No se pudo conectar con la API en {BASE_URL}. ¿Está corriendo uvicorn?")
        sys.exit(2)

    # --- Consulta sin datos (base vacía) ---
    st, g = llamar("GET", "/graph")
    if g["nodes"]:
        print("La base no está vacía: reinicie la API con una base nueva y vuelva a ejecutar.")
        sys.exit(1)
    st, cuerpo = llamar("GET", f"/impact/{FANTASMA}")
    escenario("Consulta sin datos: impacto en un catálogo vacío",
              "404 ERR_ELEMENT_NOT_FOUND", f"{st} {codigo_error(cuerpo)}",
              st == 404 and codigo_error(cuerpo) == "ERR_ELEMENT_NOT_FOUND")

    # --- Preparación del escenario normal ---
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
    listo = all(ids.values()) and all(s == 201 for s in estados)
    escenario("Preparación: 9 elementos y 8 dependencias",
              "todos creados con 201",
              f"{sum(1 for v in ids.values() if v)} elementos, {estados.count(201)} dependencias",
              listo)
    if not listo:
        print("No se pudo preparar el escenario; no tiene sentido seguir.")
        sys.exit(1)

    # --- Escenario normal: falla de un proveedor ---
    st, r = impacto(ids, "Molinos SA")
    niveles = por_nivel(r) if st == 200 else []
    escenario("Normal: si falla Molinos SA, se afecta toda la cadena que lo usa",
              "200 chain, 5 afectados en 3 niveles: {Harina, Levadura} → {Masa madre, Torta} → {Pan}",
              f"{st} {r.get('outcome')}, {r.get('affected_count')} afectados en {r.get('max_level')} niveles: {niveles}",
              st == 200 and r["outcome"] == "chain" and r["affected_count"] == 5 and r["max_level"] == 3
              and niveles == [{"Harina", "Levadura"}, {"Masa madre", "Torta"}, {"Pan"}])

    pan = next((e for n in r["levels"] for e in n["elements"] if e["name"] == "Pan"), None) if st == 200 else None
    escenario("Normal: cada elemento afectado trae su ruta y la frase del negocio",
              "ruta que empieza en Molinos SA y termina en Pan (4 nombres); razón 'Para producir Pan necesito Masa madre'",
              f"ruta={pan and pan['path']}, razón={pan and pan['reason']!r}",
              pan is not None and len(pan["path"]) == 4 and pan["path"][0] == "Molinos SA"
              and pan["path"][-1] == "Pan" and pan["reason"] == "Para producir Pan necesito Masa madre")

    # --- Normal: falla de un insumo ---
    st, r = impacto(ids, "Harina")
    escenario("Normal: si falta Harina, se afectan Masa madre, Torta y Pan",
              "chain, 3 afectados en 2 niveles: {Masa madre, Torta} → {Pan}",
              f"{r.get('outcome')}, {r.get('affected_count')} afectados en {r.get('max_level')} niveles: {por_nivel(r) if st == 200 else None}",
              st == 200 and r["outcome"] == "chain" and r["affected_count"] == 3
              and por_nivel(r) == [{"Masa madre", "Torta"}, {"Pan"}])

    # --- Relación inexistente: dos elementos que existen pero no están conectados ---
    st, r = impacto(ids, "Granja El Roble")
    afectados = nombres(r) if st == 200 else []
    escenario("Relación inexistente: la falla de Granja El Roble no alcanza a Pan",
              "afecta {Huevos, Torta}; Pan, Masa madre y Panela no aparecen",
              f"afectados={afectados}",
              st == 200 and set(afectados) == {"Huevos", "Torta"})

    # --- Consulta hacia un producto ---
    st, r = impacto(ids, "Pan", "requirements")
    escenario("Normal: ¿qué necesita Pan para producirse? (modo requirements)",
              "chain, 4 elementos en 3 niveles: {Masa madre} → {Harina, Levadura} → {Molinos SA}",
              f"{r.get('outcome')}, {r.get('affected_count')} elementos en {r.get('max_level')} niveles: {por_nivel(r) if st == 200 else None}",
              st == 200 and r["outcome"] == "chain" and r["affected_count"] == 4
              and por_nivel(r) == [{"Masa madre"}, {"Harina", "Levadura"}, {"Molinos SA"}])

    # --- Elemento sin dependencias vs. elemento que no alcanza a nadie ---
    st, r = impacto(ids, "Panela")
    escenario("Sin dependencias: Panela no necesita nada ni nadie la necesita",
              "200 isolated, 0 afectados",
              f"{st} {r.get('outcome')}, {r.get('affected_count')} afectados",
              st == 200 and r["outcome"] == "isolated" and r["affected_count"] == 0 and r["levels"] == [])

    st, r = impacto(ids, "Pan")
    escenario("Sin alcance: si falla Pan no se afecta a nadie (producto final)",
              "200 no_reach, 0 afectados",
              f"{st} {r.get('outcome')}, {r.get('affected_count')} afectados",
              st == 200 and r["outcome"] == "no_reach" and r["affected_count"] == 0)

    st, r = impacto(ids, "Molinos SA", "requirements")
    escenario("Sin alcance: Molinos SA no necesita nada para 'producirse' (proveedor)",
              "200 no_reach, 0 elementos",
              f"{st} {r.get('outcome')}, {r.get('affected_count')} elementos",
              st == 200 and r["outcome"] == "no_reach" and r["affected_count"] == 0)

    # --- Elemento inexistente (con datos cargados) ---
    st, cuerpo = llamar("GET", f"/impact/{FANTASMA}")
    escenario("Elemento inexistente: id que no está en el catálogo",
              "404 ERR_ELEMENT_NOT_FOUND", f"{st} {codigo_error(cuerpo)}",
              st == 404 and codigo_error(cuerpo) == "ERR_ELEMENT_NOT_FOUND")

    # --- Datos inválidos ---
    st, cuerpo = llamar("GET", "/impact/abc")
    escenario("Dato inválido: id mal formado",
              "422 ERR_VALIDATION con message", f"{st} {codigo_error(cuerpo)}",
              st == 422 and codigo_error(cuerpo) == "ERR_VALIDATION" and "message" in cuerpo)

    st, cuerpo = llamar("GET", f"/impact/{ids['Pan']}?mode=otracosa")
    escenario("Dato inválido: modo de consulta desconocido",
              "422 ERR_VALIDATION con message", f"{st} {codigo_error(cuerpo)}",
              st == 422 and codigo_error(cuerpo) == "ERR_VALIDATION" and "message" in cuerpo)

    # --- Ciclo: el recorrido debe terminar y no repetir elementos ---
    st, _ = llamar("POST", "/dependencies",
                   {"requiring_element_id": ids["Masa madre"], "required_element_id": ids["Pan"]})
    escenario("Ciclo: se registra 'Masa madre necesita Pan' (Pan ya necesitaba Masa madre)",
              "201 (F1 lo guarda; la alerta del ciclo corresponde a F3)", st, st == 201)

    st, r = impacto(ids, "Molinos SA")
    lista = nombres(r) if st == 200 else []
    escenario("Ciclo: el impacto de Molinos SA termina y no repite elementos",
              "200, 5 afectados sin repetidos",
              f"{st}, {len(lista)} afectados, {len(set(lista))} distintos",
              st == 200 and len(lista) == 5 and len(set(lista)) == 5)

    st, r = impacto(ids, "Pan")
    lista = nombres(r) if st == 200 else []
    escenario("Ciclo: el origen no aparece como afectado de sí mismo",
              "200, afectados = [Masa madre] (Pan no se cuenta)",
              f"{st}, afectados={lista}",
              st == 200 and lista == ["Masa madre"])

    # --- Resumen ---
    total, ok = len(resultados), sum(resultados)
    print(f"Resultado: {ok}/{total} escenarios pasaron")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()

