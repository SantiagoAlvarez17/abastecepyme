# AbastecePyme Backend

API REST de AbastecePyme. Incluye el catálogo de dependencias (Feature 1), el análisis de impacto y requisitos (Feature 2) y el orden de preparación con detección de ciclos (Feature 3). Está organizada con Clean Architecture (FastAPI + SQLAlchemy).

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
| GET | `/production-order` | Orden de preparación válido de todo el catálogo, o `409` con el ciclo exacto si las dependencias se contradicen (Feature 3) |

`GET /impact/{element_id}` utiliza el recorrido BFS propio `DependencyGraph.reach` y devuelve:
- `mode`: `"impact"` o `"requirements"`
- `origin` / `element`: datos del elemento consultado
- `outcome`: `"chain"` (alcanza una cadena), `"isolated"` (elemento sin ninguna arista entrante ni saliente) o `"no_reach"` (tiene aristas, pero no en la dirección consultada)
- `summary` / `message`: explicación legible del resultado
- `affected_count`, `max_level`, `affected_by_type`
- `levels`: lista de niveles (`level`, `label`, `elements`), donde cada elemento alcanzado incluye `id`, `name`, `element_type`, `level`, `via_id`, `reason` (*"Para producir X necesito Y"*) y `path` (ruta completa desde el origen)
- `visited_elements`: lista plana en orden BFS

Un elemento inexistente o inactivo responde `404 ERR_ELEMENT_NOT_FOUND`.

`GET /production-order` genera el orden de trabajo con un ordenamiento topológico propio (`DependencyGraph.preparation_order`) y devuelve:
- `total_elements` y `stage_count`
- `summary`: explicación legible del resultado
- `steps`: el orden de trabajo. Cada paso incluye `position` (lugar en el orden), `stage` (etapa), `id`, `name`, `element_type` y `requires` (nombres de sus requisitos directos, todos anteriores en el orden)

Los pasos de una misma etapa no dependen entre sí y pueden prepararse en paralelo. Un catálogo vacío responde 200 con `steps: []`. Este endpoint no recibe parámetros, por lo que no tiene casos de elemento inexistente ni de identificador inválido.

Si las dependencias forman un ciclo no existe un orden válido: responde `409 ERR_CYCLE_DETECTED` y **no devuelve ningún orden**. El cuerpo explica la contradicción:
- `message`: texto legible que empieza por la ruta cerrada (`Ciclo detectado: Masa madre → Pan → Masa madre.`) y, aparte, los elementos que solo dependen del ciclo. Con varios ciclos empieza por `Ciclos detectados (2): 1) ... 2) ...`.
- `cycles`: lista de ciclos. Cada uno trae `text` y `elements` (`id`, `name`, `element_type`), como camino cerrado en el sentido de las dependencias: el primer elemento se repite al final. Hay un ciclo por cada grupo de elementos que se necesitan entre sí.
- `blocked_by_cycle`: elementos que no forman parte de ningún ciclo, pero quedan sin orden porque dependen de uno.

Los errores siempre responden con `{error_code, message}`:

| Código HTTP | `error_code` | Cuándo |
|---|---|---|
| 404 | `ERR_ELEMENT_NOT_FOUND` | El elemento consultado o uno de los extremos de la dependencia no existe |
| 409 | `ERR_DUPLICATE_ELEMENT` | Ya existe un elemento con ese nombre |
| 409 | `ERR_DUPLICATE_DEPENDENCY` | La relación ya estaba registrada |
| 409 | `ERR_CYCLE_DETECTED` | Las dependencias forman un ciclo y no existe un orden de preparación válido (`GET /production-order`) |
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
- Consultas disponibles: `requirements_of`, `dependents_of`, `reach` (BFS propio que devuelve `Visit(node_id, level, via_id)`), `reachable_from`, `has_path` (DFS iterativo) y `would_create_cycle` (disponible, pero F1 no la usa para rechazar: los ciclos se registran y los reporta F3) y `preparation_order` (F3).
- Ocupa `O(V + E)` en memoria, el acceso a los vecinos de un nodo es `O(grado)` y los recorridos `reach` / `has_path` son `O(V + E)`.
- La base SQL solo sirve para persistir. El grafo se reconstruye en memoria en cada consulta.

**Ciclos:**
- F1 rechaza la autodependencia directa (`A → A`).
- Los ciclos más largos (`Pan → Masa madre → Pan`) se **registran**: `reach` en F2 los recorre sin colgarse ni repetir nodos y F3 los detecta y los reporta. Si F1 los rechazara, el caso cíclico no podría existir en los datos.

**Orden de preparación (F3).** Como `A → B` significa "para producir A necesito B", **B debe prepararse antes que A**. El orden se calcula con el algoritmo de Kahn por etapas, propio y sin librerías: se cuentan los requisitos pendientes de cada elemento; en cada etapa se toman los que no tienen ninguno (proveedores, insumos sin proveedor y elementos aislados en la primera) y, al prepararlos, se descuenta un requisito pendiente a quienes los necesitan (índice `_required_by`). Los que llegan a cero forman la etapa siguiente. Dentro de cada etapa los elementos se ordenan por tipo y nombre, así que el resultado es siempre el mismo. Complejidad: `O(V + E)` del recorrido más `O(V log V)` de ordenar las etapas.

**Detección y reporte del ciclo (F3).** Si al terminar quedan elementos con requisitos pendientes, hay una contradicción y no se inventa un orden: esos elementos quedan en `OrderingResult.blocked`. Pero "bloqueado" no es lo mismo que "parte del ciclo": un producto que solo depende de un elemento del ciclo también queda bloqueado. Para distinguirlos:
1. Sobre el subgrafo de los bloqueados se calculan los **grupos de elementos que se necesitan entre sí** (componentes fuertemente conexos) con el algoritmo de **Tarjan**, en versión iterativa para no depender de la recursión de Python. Un grupo de un solo elemento solo cuenta como ciclo si se requiere a sí mismo.
2. Por cada grupo se reconstruye el **ciclo más corto** que pasa por su primer elemento, con un recorrido en anchura dentro del grupo. Es un camino cerrado en el sentido de las aristas: `[Pan, Masa madre, Pan]` = "Pan necesita Masa madre y Masa madre necesita Pan".
3. Los bloqueados que quedan fuera de todo grupo se informan aparte (`blocked_by_cycle`): dependen del ciclo, pero no lo forman.

`OrderingResult.cycle` (el primer ciclo reportado, introducido en `feature/orden-produccion-ciclos`) se conserva como atajo para quien solo necesite uno. Se informa un ciclo representativo por grupo, no todos los ciclos posibles: enumerarlos es exponencial y, para corregir la contradicción, basta ver uno de cada grupo (al corregirlo, la siguiente consulta mostrará el que quede). Complejidad: `O(V + E)` para los grupos y `O(V + E)` por cada ciclo reconstruido. Todo el resultado es determinista: no cambia con el orden de registro.

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
2. En otra terminal, ejecute el script de la feature que quiera probar:
   ```bash
   python scripts/aceptacion_f1.py
   ```
3. Para probar la Feature 2, borre `aceptacion.db`, reinicie la API y ejecute:
   ```bash
   python scripts/aceptacion_f2.py
   ```
4. Para probar la Feature 3, borre `aceptacion.db`, reinicie la API y ejecute:
   ```bash
   python scripts/aceptacion_f3.py
   ```
   El script prueba un caso acíclico y uno cíclico, y termina registrando un ciclo, así que la base debe borrarse antes de volver a ejecutarlo.

## Pruebas unitarias y de integración (`pytest`)
`tests/` contiene pruebas del grafo (incluidos el orden de preparación y el reporte de ciclos, con pruebas de propiedad sobre grafos aleatorios), de los casos de uso con repositorios en memoria y de los endpoints HTTP:
```bash
pip install -r requirements-dev.txt
python -m pytest tests
```
