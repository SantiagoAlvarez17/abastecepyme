"""
Carga de datos sintéticos — Feature 1: Catálogo de dependencias.

Escenario ficticio: "PanArte", una panadería-pastelería pequeña. Todos los
nombres son inventados; no hay datos personales reales.

Consume la API REST real, igual que scripts/aceptacion_f1.py. Se puede ejecutar
varias veces: lo que ya existe se reutiliza y no se duplica.

Uso:
    python scripts/cargar_datos_ejemplo.py [URL_BASE]   (por defecto http://localhost:8000)
"""
import json
import sys
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

# Cada insumo depende de un proveedor; cada producto, de insumos u otros productos.
PROVEEDORES = [
    "Molinos del Valle",
    "Lácteos Andinos",
    "Granja El Roble",
    "Ingenio Dulce",
    "Fermentos del Sur",
    "Empaques del Norte",
]

# insumo -> proveedor del que depende
INSUMOS = {
    "Harina de trigo": "Molinos del Valle",
    "Mantequilla": "Lácteos Andinos",
    "Leche": "Lácteos Andinos",
    "Huevos": "Granja El Roble",
    "Azúcar": "Ingenio Dulce",
    "Levadura": "Fermentos del Sur",
    "Bolsas de papel": "Empaques del Norte",
}

# producto -> lo que necesita (insumos u otros productos)
PRODUCTOS = {
    "Masa madre": ["Harina de trigo", "Levadura"],
    "Pan": ["Masa madre", "Bolsas de papel"],
    "Croissant": ["Masa madre", "Mantequilla", "Bolsas de papel"],
    "Torta de vainilla": ["Harina de trigo", "Huevos", "Azúcar", "Mantequilla", "Leche", "Bolsas de papel"],
    "Combo desayuno": ["Croissant", "Pan"],
}


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


def codigo_error(cuerpo):
    return cuerpo.get("error_code") if isinstance(cuerpo, dict) else None


def asegurar_elemento(nombre, tipo, existentes):
    """Crea el elemento o reutiliza el que ya existe. Devuelve (id, fue_creado)."""
    st, cuerpo = llamar("POST", "/elements", {"name": nombre, "element_type": tipo})
    if st == 201:
        return cuerpo["id"], True
    if st == 409 and codigo_error(cuerpo) == "ERR_DUPLICATE_ELEMENT":
        return existentes[nombre.lower()], False
    raise RuntimeError(f"No se pudo crear '{nombre}': {st} {cuerpo}")


def asegurar_dependencia(nombre_requiere, nombre_requerido, ids):
    """Registra 'Para producir A necesito B'. Devuelve True si fue creada, False si ya existía."""
    st, cuerpo = llamar("POST", "/dependencies", {
        "requiring_element_id": ids[nombre_requiere],
        "required_element_id": ids[nombre_requerido],
    })
    if st == 201:
        return True
    if st == 409 and codigo_error(cuerpo) == "ERR_DUPLICATE_DEPENDENCY":
        return False
    raise RuntimeError(f"No se pudo registrar '{nombre_requiere}' -> '{nombre_requerido}': {st} {cuerpo}")


def main():
    try:
        st, elementos = llamar("GET", "/elements")
    except urllib.error.URLError:
        print(f"No se pudo conectar con la API en {BASE_URL}. ¿Está corriendo uvicorn?")
        sys.exit(2)

    existentes = {e["name"].lower(): e["id"] for e in elementos}
    ids = {}
    elementos_creados = 0
    dependencias_creadas = 0

    plan = (
        [(n, "proveedor") for n in PROVEEDORES]
        + [(n, "insumo") for n in INSUMOS]
        + [(n, "producto") for n in PRODUCTOS]
    )
    for nombre, tipo in plan:
        ids[nombre], creado = asegurar_elemento(nombre, tipo, existentes)
        elementos_creados += creado

    for insumo, proveedor in INSUMOS.items():
        dependencias_creadas += asegurar_dependencia(insumo, proveedor, ids)
    for producto, necesidades in PRODUCTOS.items():
        for necesidad in necesidades:
            dependencias_creadas += asegurar_dependencia(producto, necesidad, ids)

    total_dependencias = len(INSUMOS) + sum(len(v) for v in PRODUCTOS.values())
    print(f"Elementos:    {len(plan)} en el escenario ({elementos_creados} nuevos, {len(plan) - elementos_creados} ya existían)")
    print(f"Dependencias: {total_dependencias} en el escenario ({dependencias_creadas} nuevas, {total_dependencias - dependencias_creadas} ya existían)")

    st, grafo = llamar("GET", "/graph")
    print(f"GET /graph:   {len(grafo['nodes'])} nodos y {len(grafo['edges'])} aristas en la base")


if __name__ == "__main__":
    main()