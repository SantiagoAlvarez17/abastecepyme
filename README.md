# AbastecePyme

Microproducto para una pyme que fabrica productos sencillos. Le permite registrar **proveedores, insumos y productos** y las **dependencias** entre ellos, para después analizar qué se afecta cuando falla un proveedor y en qué orden conviene preparar la producción.

**Feature 1 — Catálogo de dependencias:** crear y listar elementos, registrar dependencias válidas, rechazar duplicados y datos mal formados, y ver la red mediante la API y una interfaz.

## Estructura
| Carpeta | Contenido |
|---|---|
| `backend/` | API REST en Python (FastAPI). Incluye el grafo propio y el script de aceptación. Ver [backend/README.md](backend/README.md) |
| `ui/` | Interfaz mínima en Streamlit que consume la API |
| `docs/` | [Bitácora de uso de IA](docs/bitacora-ia.md) |

## Cómo ejecutar (Windows, Python 3.12+)

**1. Crear el entorno e instalar dependencias** (una sola vez, desde la raíz del proyecto):
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt -r ui/requirements.txt
```

**2. Levantar el backend:**
```bash
cd backend
uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000
```

**3. En otra terminal, levantar la interfaz:**
```bash
.venv\Scripts\activate
streamlit run ui/app.py
```
Se abre en http://localhost:8501. Si la API está en otra dirección, defina antes `set API_URL=http://...`.

**4. Pruebas de aceptación:** ver la sección correspondiente en [backend/README.md](backend/README.md).

## Modelo del grafo (resumen)
- **Nodos:** proveedores, insumos y productos.
- **Aristas dirigidas:** `A → B` = "Para producir A necesito B". Por ejemplo, `Pan → Harina → Molinos SA`.
- **Representación:** lista de adyacencia propia (`DependencyGraph`), sin librerías de grafos.
- **Interfaz:** la red se dibuja con Graphviz a partir de lo que devuelve `GET /graph`. La interfaz no calcula nada del grafo por su cuenta.
