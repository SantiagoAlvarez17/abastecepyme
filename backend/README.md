# AbastecePyme Backend

API REST de AbastecePyme. Incluye el catálogo de dependencias (Feature 1) y el análisis de impacto y requisitos (Feature 2). Está organizada con Clean Architecture (FastAPI + SQLAlchemy).

## Requisitos
- Python 3.12 o superior
- Dependencias listadas en `requirements.txt`

## Instalación (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución
```bash
uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000
```
Por defecto la base es SQLite (`abastecepyme.db`). Para usar otro archivo, defina `DATABASE_URL`.
La documentación interactiva queda en http://localhost:8000/docs

## Endpoints
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/elements` | Crea un elemento `{name, element_type}` (`proveedor`, `insumo`, `producto`) |
| GET | `/elements` | Lista los elementos activos |
| POST | `/dependencies` | Registra `{requiring_element_id, required_element_id}` |
| GET | `/dependencies` | Lista las aristas |
| GET | `/graph` | Red completa: nodos, aristas y lista de adyacencia |
| GET | `/impact/{element_id}` | Analiza qué se afecta si el elemento no está disponible (`mode=impact`, por defecto) |
| GET | `/impact/{element_id}?mode=requirements` | Analiza qué necesita el elemento para producirse (`mode=requirements`) |

`GET /impact/{element_id}` utiliza el recorrido BFS propio `DependencyGraph.reach` y devuelve:
- `mode`: `"impact"` o `"requirements"`
- `origin` / `element`: datos del elemento consultado
- `outcome`: `"chain"` (alcanza una cadena), `"isolated"` (elemento sin ninguna arista entrante ni saliente) o `"no_reach"` (tiene aristas, pero no en la dirección consultada)
- `summary` / `message`: explicación legible del resultado
- `affected_count`, `max_level`, `affected_by_type`
- `levels`: lista de niveles (`level`, `label`, `elements`), donde cada elemento alcanzado incluye `id`, `name`, `element_type`, `level`, `via_id`, `reason` (*"Para producir X necesito Y"*) y `path` (ruta completa desde el origen)
- `visited_elements`: lista plana en orden BFS

Un elemento inexistente o inactivo responde `404 ERR_ELEMENT_NOT_FOUND`.

Los errores siempre responden con `{error_code, message}`:

| Código HTTP | `error_code` | Cuándo |
|---|---|---|
| 404 | `ERR_ELEMENT_NOT_FOUND` | El elemento consultado o uno de los extremos de la dependencia no existe |
| 409 | `ERR_DUPLICATE_ELEMENT` | Ya existe un elemento con ese nombre |
| 409 | `ERR_DUPLICATE_DEPENDENCY` | La relación ya estaba registrada |
| 400 | `ERR_SELF_DEPENDENCY` | Un elemento se requiere a sí mismo |
| 400 | `ERR_INVALID_DEPENDENCY_TYPE` | La combinación de tipos no tiene sentido de negocio |
| 422 | `ERR_VALIDATION` | Datos mal formados: campo faltante, tipo inválido, id que no es UUID, `mode` inválido o nombre vacío |

## Decisiones de diseño

**Dirección de las aristas: `A → B` significa "Para producir A necesito B".**
Ejemplo: `Pan → Masa madre → Harina → Molinos SA`. La frase invertida ("Para producir Harina necesito Pan") no tiene sentido, por eso el grafo es dirigido.
Consecuencia para F2: cuando falla un proveedor, insumo o producto intermedio, el impacto se calcula recorriendo las aristas en sentido contrario (`mode=impact`), hacia quienes lo necesitan. Cuando se consulta qué requiere un elemento para producirse (`mode=requirements`), se recorren las aristas en su dirección definida. El modelo resuelve ambos sentidos con sus dos listas de adyacencia (`_required_by` y `_requires`), sin condicionales por tipo de elemento.

**Qué significa "alcanzar":**
En el negocio de AbastecePyme, **alcanzar** significa que existe un camino dirigido de una o más relaciones *"Para producir A necesito B"* entre el elemento consultado y otro. Los elementos alcanzados se organizan por niveles de proximidad (nivel 1: afectación/requisito directo; nivel 2+: afectación/requisito en cadena). El recorrido usa un conjunto de visitados, por lo que no repite elementos y termina incluso si existen ciclos.

**Reglas de tipos:**
- Un proveedor no depende de nada.
- Un insumo solo depende de proveedores.
- Un producto depende de insumos o de otros productos (productos intermedios).

**Identificador único:**
- El `id` es un UUID interno.
- El identificador de negocio es el **nombre**: único, sin distinguir mayúsculas y sin espacios al inicio o al final.

**Representación principal:**
- La clase propia `DependencyGraph` (`domain/graph/dependency_graph.py`) implementa **listas de adyacencia** con dos índices:
  - `_requires: dict[id, list[id]]`: aristas salientes, lo que cada elemento necesita. Es lo que expone `adjacency` en `GET /graph`.
  - `_required_by: dict[id, list[id]]`: aristas entrantes, quién necesita a cada elemento. Permite recorrer el grafo al revés (`mode=impact` en F2) sin recalcular nada.
- Consultas disponibles: `requirements_of`, `dependents_of`, `reach` (BFS propio que devuelve `Visit(node_id, level, via_id)`), `reachable_from`, `has_path` (DFS iterativo) y `would_create_cycle` (preparada para F3).
- Ocupa `O(V + E)` en memoria, el acceso a los vecinos de un nodo es `O(grado)` y los recorridos `reach` / `has_path` son `O(V + E)`.
- La base SQL solo sirve para persistir. El grafo se reconstruye en memoria en cada consulta.

**Ciclos:**
- F1 rechaza la autodependencia directa (`A → A`).
- Los ciclos más largos (`Pan → Masa madre → Pan`) se registran y `reach` en F2 los recorre sin colgarse ni repetir nodos. Detectarlos y alertar corresponde a F3.

## Datos de ejemplo
Para cargar un escenario sintético (una panadería ficticia con 6 proveedores, 7 insumos y 5 productos), con la API levantada:
```bash
python scripts/cargar_datos_ejemplo.py
```
Se puede ejecutar varias veces: lo que ya existe no se duplica. No lo use sobre la base de las pruebas de aceptación, que debe estar vacía.

## Pruebas de aceptación
1. Levante la API sobre una base vacía:
   ```bash
   del aceptacion.db
   set DATABASE_URL=sqlite:///./aceptacion.db
   uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000
   ```
2. En otra terminal, ejecute:
   ```bash
   python scripts/aceptacion_f1.py
   ```
   Para probar la Feature 2, borre `aceptacion.db`, reinicie la API y ejecute:
   ```bash
   python scripts/aceptacion_f2.py
   ```

## Pruebas unitarias y de integración (`pytest`)
`tests/` contiene pruebas del grafo, del caso de uso de impacto con repositorios en memoria y de los endpoints HTTP:
```bash
pip install -r requirements-dev.txt
python -m pytest tests
```
