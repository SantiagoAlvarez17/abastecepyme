"""
Interfaz mínima de AbastecePyme — Features 1 y 2: Catálogo y análisis de impacto.

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
MODOS_IMPACTO = {
    "impact": "Impacto de indisponibilidad (¿qué se afecta si falla?)",
    "requirements": "Requisitos de producción (¿qué necesito para producirlo?)",
}


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


def dot_del_grafo(grafo, analisis=None):
    """Traduce la respuesta de GET /graph a lenguaje DOT, resaltando la cadena consultada si existe."""
    origen_id = analisis["origin"]["id"] if analisis else None
    nivel_por_id = {}
    aristas_recorridas = set()

    if analisis:
        es_impacto = analisis.get("mode") == "impact"
        for nivel in analisis.get("levels", []):
            for elem in nivel.get("elements", []):
                nivel_por_id[elem["id"]] = elem["level"]
                if es_impacto:
                    aristas_recorridas.add((elem["id"], elem["via_id"]))
                else:
                    aristas_recorridas.add((elem["via_id"], elem["id"]))

    lineas = [
        "digraph G {",
        "  rankdir=LR;",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica"];',
        '  edge [fontname="Helvetica", fontsize=10, color="#666666"];',
    ]
    for n in grafo["nodes"]:
        nid = n["id"]
        nombre = n["name"].replace('"', '\\"')
        etiqueta_nodo = f"{nombre}\\n({n['element_type']})"
        atributos = [f'fillcolor="{COLOR_TIPO[n["element_type"]]}"']

        if nid == origen_id:
            etiqueta_nodo += "\\n[Origen consultado]"
            atributos.append('color="#B4637A"')
            atributos.append("penwidth=3.0")
        elif nid in nivel_por_id:
            etiqueta_nodo += f"\\n[Nivel {nivel_por_id[nid]}]"
            atributos.append('color="#286983"')
            atributos.append("penwidth=2.5")

        lineas.append(f'  "{nid}" [label="{etiqueta_nodo}", {", ".join(atributos)}];')

    for e in grafo["edges"]:
        par = (e["requiring_element_id"], e["required_element_id"])
        if par in aristas_recorridas:
            lineas.append(
                f'  "{par[0]}" -> "{par[1]}" '
                '[label="necesita", color="#B4637A", fontcolor="#B4637A", penwidth=2.2];'
            )
        else:
            lineas.append(f'  "{par[0]}" -> "{par[1]}" [label="necesita"];')
    lineas.append("}")
    return "\n".join(lineas)


def mostrar_resultado():
    """Muestra el mensaje de la última acción (sobrevive al st.rerun)."""
    if "resultado" in st.session_state:
        ok, texto = st.session_state.pop("resultado")
        (st.success if ok else st.error)(texto)


st.set_page_config(page_title="AbastecePyme — Catálogo e Impacto", page_icon="🏭", layout="wide")
st.title("AbastecePyme — Catálogo y Análisis de Impacto")
st.caption("Dirección de las aristas: **A → B** significa *“Para producir A necesito B”*.")

ok_grafo, grafo = llamar("GET", "/graph")
if not ok_grafo:
    st.error(grafo)
    st.stop()

nodos = grafo["nodes"]
por_id = {n["id"]: n for n in nodos}


def etiqueta(i):
    return f"{por_id[i]['name']} ({por_id[i]['element_type']})"


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
analisis_activo = st.session_state.get("analisis_impacto")
if analisis_activo and analisis_activo["origin"]["id"] not in por_id:
    analisis_activo = None
    st.session_state.pop("analisis_impacto", None)

if not nodos:
    st.info("El catálogo está vacío. Registre proveedores, insumos y productos para ver la red.")
else:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Elementos", len(nodos))
    m2.metric("Dependencias", len(grafo["edges"]))
    m3.metric("Productos", sum(n["element_type"] == "producto" for n in nodos))
    m4.metric("Proveedores", sum(n["element_type"] == "proveedor" for n in nodos))

    st.graphviz_chart(dot_del_grafo(grafo, analisis_activo), width="stretch")
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

st.divider()

# --- Analizar impacto (Feature 2) ---
st.subheader("4. Analizar impacto")
st.caption(
    "Consulte qué productos o procesos se afectan ante la indisponibilidad de un elemento (`mode=impact`) "
    "o qué necesita un elemento para producirse (`mode=requirements`)."
)
if not nodos:
    st.info("Registre elementos y dependencias para consultar el análisis de impacto.")
else:
    opciones_impacto = sorted(
        nodos,
        key=lambda n: (TIPOS.index(n["element_type"]), n["name"].lower()),
    )
    col_sel, col_modo = st.columns(2)
    with col_sel:
        id_impacto = st.selectbox(
            "Elemento para analizar",
            [n["id"] for n in opciones_impacto],
            format_func=etiqueta,
            key="impact_element",
        )
    with col_modo:
        modo_por_defecto = 1 if por_id[id_impacto]["element_type"] == "producto" else 0
        modo_impacto = st.selectbox(
            "Sentido de la consulta",
            list(MODOS_IMPACTO.keys()),
            index=modo_por_defecto,
            format_func=MODOS_IMPACTO.get,
            key="impact_mode",
        )

    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    if col_btn1.button("Analizar cadena"):
        ok, resultado = llamar("GET", f"/impact/{id_impacto}?mode={modo_impacto}")
        if ok:
            st.session_state["analisis_impacto"] = resultado
            st.rerun()
        else:
            st.error(resultado)

    if analisis_activo and col_btn2.button("Limpiar resaltado"):
        st.session_state.pop("analisis_impacto", None)
        st.rerun()

    if analisis_activo:
        outcome = analisis_activo["outcome"]
        resumen = analisis_activo["summary"]

        if outcome == "chain":
            if analisis_activo["mode"] == "impact":
                st.warning(f"**{analisis_activo['origin']['name']}** · {resumen}")
            else:
                st.info(f"**{analisis_activo['origin']['name']}** · {resumen}")
        elif outcome == "isolated":
            st.info(f"**Elemento sin dependencias (aislado):** {resumen}")
        else:
            st.success(f"**Sin alcance en esta dirección:** {resumen}")

        st.caption(f"Dirección recorrida: {analisis_activo['direction']}.")

        if analisis_activo["levels"]:
            c1, c2, c3 = st.columns(3)
            c1.metric("Elementos alcanzados", analisis_activo["affected_count"])
            c2.metric("Niveles de la cadena", analisis_activo["max_level"])
            desglose = ", ".join(
                f"{cant} {ETIQUETA_TIPO.get(t, t).lower()}(s)"
                for t, cant in analisis_activo["affected_by_type"].items()
            )
            c3.metric("Por tipo", desglose or "—")

            for nivel in analisis_activo["levels"]:
                st.markdown(f"#### Nivel {nivel['level']} — {nivel['label']}")
                for elem in nivel["elements"]:
                    ruta = " → ".join(elem["path"])
                    st.markdown(
                        f"- **{elem['name']}** ({ETIQUETA_TIPO[elem['element_type']]})  \n"
                        f"  *Razón:* {elem['reason']} · *Ruta:* `{ruta}`"
                    )
