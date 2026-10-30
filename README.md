# AbastecePyme

Microproducto para una pyme que fabrica productos sencillos. Le permite registrar **proveedores, insumos y productos** y las **dependencias** entre ellos, para después analizar qué se afecta cuando falla un proveedor o insumo y qué necesita cada producto.

**Feature 1 — Catálogo de dependencias:** crear y listar elementos, registrar dependencias válidas, rechazar duplicados y datos mal formados, y ver la red mediante la API y la interfaz.
**Feature 2 — Análisis de impacto:** recorrer la cadena relacionada con un proveedor, insumo o producto (por niveles, con ruta y razón de negocio), tanto mediante la API como desde la interfaz con resaltado en el grafo.

## Estructura
| Carpeta | Contenido |
|---|---|
| `backend/` | API REST en Python (FastAPI). Incluye el grafo propio y los scripts de aceptación (`aceptacion_f1.py` y `aceptacion_f2.py`). Ver [backend/README.md](backend/README.md) |
| `frontend/` | Interfaz web empresarial en Next.js + Tailwind + React Flow con vistas por rol (**Compras** y **Producción**). Ver [frontend/README.md](frontend/README.md) |
| `ui/` | Interfaz alternativa ligera en Streamlit que consume la misma API |
| `docs/` | [Bitácora de uso de IA](docs/bitacora-ia.md) |

## Cómo ejecutar (Windows, Python 3.12+ y Node.js 20+)

**1. Crear el entorno de Python e instalar dependencias del backend:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt -r ui/requirements.txt
```

**2. Levantar el backend (`http://localhost:8000`):**
```bash
cd backend
uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000
```

**3. Levantar el frontend empresarial en Next.js (`http://localhost:3000`):**
```bash
cd frontend
npm install
npm run dev
```
*(Opcionalmente, también puede usar la interfaz ligera en Streamlit ejecutando `streamlit run ui/app.py` en `http://localhost:8501`).*

**4. Pruebas de aceptación:** ver la sección correspondiente más abajo y en [backend/README.md](backend/README.md).

## Modelo del grafo (resumen)
- **Nodos:** proveedores, insumos y productos.
- **Aristas dirigidas:** `A → B` = *"Para producir A necesito B"*. Por ejemplo, `Pan → Masa madre → Harina → Molinos SA`.
- **Representación:** listas de adyacencia propias (`DependencyGraph`), una de salida (`_requires`) y otra inversa (`_required_by`), sin librerías de grafos.
- **Interfaz:** la red se dibuja a partir de lo que devuelve `GET /graph`, y el análisis de impacto consume `GET /impact/{element_id}` resaltando el origen, los niveles alcanzados y las aristas recorridas. La interfaz no calcula los recorridos por su cuenta.

## Análisis de impacto (Feature 2)

**¿Qué significa "alcanzar" en este negocio?** Un elemento `Y` es alcanzado desde `X` cuando existe una cadena de una o más relaciones *"Para producir A necesito B"* que los conecta en el sentido de la consulta. El **nivel 1** representa la relación directa, el **nivel 2** lo que depende del nivel 1, y así sucesivamente (dependencias transitivas). Cada elemento se reporta una sola vez con su nivel mínimo.

**Dos consultas con un solo recorrido** (`GET /impact/{element_id}?mode=impact|requirements`):

| `mode` | Pregunta de negocio | Sentido del recorrido |
|---|---|---|
| `impact` (por defecto) | Si este proveedor, insumo o producto intermedio falla, ¿qué productos y procesos se afectan? | Contra las flechas: de `B` hacia quienes lo requieren (índice `_required_by`) |
| `requirements` | Para producir este elemento, ¿qué necesito directa o indirectamente hasta llegar a los proveedores? | Con las flechas: de `A` hacia lo que requiere (índice `_requires`) |

La dirección la resuelve el modelo con sus dos listas de adyacencia, sin condicionales por tipo de elemento en el recorrido: `DependencyGraph.reach(source, reverse=...)` solo elige cuál índice seguir.

**Algoritmo:** recorrido en anchura (**BFS**) propio, con una cola (`deque`) y un conjunto de visitados (`reach` en `domain/graph/dependency_graph.py`). Complejidad `O(V + E)` en tiempo y `O(V)` en memoria. Como el conjunto de visitados evita repetir elementos, el recorrido termina aunque el catálogo contenga ciclos (F1 permite registrarlos; su detección y alerta son de F3). Se eligió BFS porque entrega los elementos por niveles, distinguiendo la afectación directa de la afectación en cadena.

**Diferenciación de escenarios:**

| Caso | Respuesta HTTP | `outcome` | Significado |
|---|---|---|---|
| El elemento no existe (o está inactivo) | `404 ERR_ELEMENT_NOT_FOUND` | — | El ID consultado no pertenece al catálogo activo |
| No tiene ninguna dependencia registrada | `200 OK` | `isolated` | El elemento está aislado: no necesita nada y nadie depende de él |
| Tiene relaciones, pero ninguna en el sentido consultado | `200 OK` | `no_reach` | P. ej., un producto final cuando se consulta quién depende de él (`impact`), o un proveedor cuando se consulta qué necesita (`requirements`) |
| Alcanza al menos un elemento | `200 OK` | `chain` | Devuelve los elementos agrupados por `levels`, con su `path` completo y la frase de negocio `reason` |

## Pruebas de aceptación

1. Levante la API sobre una base vacía:
   ```bash
   cd backend
   del aceptacion.db
   set DATABASE_URL=sqlite:///./aceptacion.db
   uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000
   ```
2. En otra terminal, ejecute el script de la Feature 1 o de la Feature 2 (borrando `aceptacion.db` y reiniciando la API entre uno y otro):
   ```bash
   python backend/scripts/aceptacion_f1.py
   ```
   ```bash
   python backend/scripts/aceptacion_f2.py
   ```
   - `aceptacion_f1.py` (25 escenarios): catálogo vacío, escenario normal, nodo inexistente, relación no registrada, relación repetida, autodependencia, identificador repetido, datos inválidos, combinación de tipos inválida y ciclo.
   - `aceptacion_f2.py` (16 escenarios): catálogo vacío, impacto por falla de proveedor e insumo por niveles con ruta y frase de negocio, relación inexistente entre cadenas separadas, consulta de requisitos de un producto (`mode=requirements`), elemento aislado (`isolated`), elemento sin alcance (`no_reach`), elemento inexistente (`404`), datos inválidos (`422`) y terminación sin repetidos en presencia de ciclos.
