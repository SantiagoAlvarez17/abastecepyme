"""
Interfaz mínima de AbastecePyme — Feature 1: Catálogo de dependencias.

Solo consume la API REST del backend; no calcula nada del grafo por su cuenta.
Ejecutar:  streamlit run ui/app.py
"""
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

TIPOS = ["proveedor", "insumo", "producto"]
ETIQUETA_TIPO = {"proveedor": "Proveedor", "insumo": "Insumo", "producto": "Producto"}
COLOR_TIPO = {"proveedor": "#F6C177", "insumo": "#9CCFD8", "producto": "#C4A7E7"}


def llamar(metodo, ruta, cuerpo=None):
    """Devuelve (ok, datos_o_mensaje)."""
    try:
        resp = requests.request(metodo, API_URL + ruta, json=cuerpo, timeout=5)
    except requests.ConnectionError:
        return False, f"No se pudo conectar con la API en {API_URL}. ¿Está corriendo el backend?"
    datos = resp.json() if resp.content else None
    if resp.ok:
        return True, datos
    mensaje = datos.get("message") if isinstance(datos, dict) else None
    return False, mensaje or f"Error {resp.status_code}"


def dot_del_grafo(grafo):
    """Traduce la respuesta de GET /graph a lenguaje DOT para dibujarla."""
    lineas = [
        "digraph G {",
        "  rankdir=LR;",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica"];',
        '  edge [fontname="Helvetica", fontsize=10, color="#666666"];',
    ]
    for n in grafo["nodes"]:
        nombre = n["name"].replace('"', '\\"')
        lineas.append(
            f'  "{n["id"]}" [label="{nombre}\\n({n["element_type"]})", '
            f'fillcolor="{COLOR_TIPO[n["element_type"]]}"];'
        )
    for e in grafo["edges"]:
        lineas.append(f'  "{e["requiring_element_id"]}" -> "{e["required_element_id"]}" [label="necesita"];')
    lineas.append("}")
    return "\n".join(lineas)


def mostrar_resultado():
    """Muestra el mensaje de la última acción (sobrevive al st.rerun)."""
    if "resultado" in st.session_state:
        ok, texto = st.session_state.pop("resultado")
        (st.success if ok else st.error)(texto)


st.set_page_config(page_title="AbastecePyme — Catálogo", page_icon="🏭", layout="wide")
st.title("AbastecePyme — Catálogo de dependencias")
st.caption("Dirección de las aristas: **A → B** significa *“Para producir A necesito B”*.")

ok_grafo, grafo = llamar("GET", "/graph")
if not ok_grafo:
    st.error(grafo)
    st.stop()

nodos = grafo["nodes"]
por_id = {n["id"]: n for n in nodos}

mostrar_resultado()

col_elem, col_dep = st.columns(2)

# --- Registrar elemento ---
with col_elem:
    st.subheader("1. Registrar elemento")
    with st.form("form_elemento", clear_on_submit=True):
        nombre = st.text_input("Nombre", placeholder="Ej.: Harina")
        tipo = st.selectbox("Tipo", TIPOS, format_func=ETIQUETA_TIPO.get)
        if st.form_submit_button("Crear elemento"):
            ok, datos = llamar("POST", "/elements", {"name": nombre, "element_type": tipo})
            st.session_state["resultado"] = (
                (True, f"Se creó {ETIQUETA_TIPO[tipo].lower()} “{datos['name']}”.") if ok else (False, datos)
            )
            st.rerun()

# --- Registrar dependencia ---
with col_dep:
    st.subheader("2. Registrar dependencia")
    if len(nodos) < 2:
        st.info("Necesita al menos dos elementos para registrar una dependencia.")
    else:
        def etiqueta(i):
            return f"{por_id[i]['name']} ({por_id[i]['element_type']})"

        ids = [n["id"] for n in sorted(nodos, key=lambda n: (TIPOS.index(n["element_type"]), n["name"].lower()))]
        # Productos primero en "Para producir…" y proveedores primero en "…necesito"
        requiere = st.selectbox("Para producir…", ids[::-1], format_func=etiqueta, key="dep_origen")
        requerido = st.selectbox("…necesito", ids, format_func=etiqueta, key="dep_destino")
        st.markdown(f"> Para producir **{por_id[requiere]['name']}** necesito **{por_id[requerido]['name']}**")
        if st.button("Registrar dependencia"):
            ok, datos = llamar("POST", "/dependencies",
                               {"requiring_element_id": requiere, "required_element_id": requerido})
            st.session_state["resultado"] = (
                (True, f"Dependencia registrada: Para producir {por_id[requiere]['name']} "
                       f"necesito {por_id[requerido]['name']}.") if ok else (False, datos)
            )
            st.rerun()

st.divider()

# --- Red de dependencias ---
st.subheader("3. Red de dependencias")
if not nodos:
    st.info("El catálogo está vacío. Registre proveedores, insumos y productos para ver la red.")
else:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Elementos", len(nodos))
    m2.metric("Dependencias", len(grafo["edges"]))
    m3.metric("Productos", sum(n["element_type"] == "producto" for n in nodos))
    m4.metric("Proveedores", sum(n["element_type"] == "proveedor" for n in nodos))

    st.graphviz_chart(dot_del_grafo(grafo), width="stretch")
    st.caption("🟧 Proveedor · 🟦 Insumo · 🟪 Producto")

    tab_frases, tab_ady, tab_elem = st.tabs(["Dependencias en frases", "Lista de adyacencia", "Elementos"])
    with tab_frases:
        if grafo["edges"]:
            for e in grafo["edges"]:
                st.markdown(f"- Para producir **{por_id[e['requiring_element_id']]['name']}** "
                            f"necesito **{por_id[e['required_element_id']]['name']}**")
        else:
            st.info("Todavía no hay dependencias registradas.")
    with tab_ady:
        st.caption("Representación principal del backend: cada elemento → lo que necesita directamente.")
        st.table([
            {
                "Elemento": por_id[i]["name"],
                "Tipo": por_id[i]["element_type"],
                "Necesita": ", ".join(por_id[v]["name"] for v in vecinos) or "—",
            }
            for i, vecinos in grafo["adjacency"].items()
        ])
    with tab_elem:
        st.table([{"Nombre": n["name"], "Tipo": n["element_type"], "ID": n["id"]} for n in nodos])
