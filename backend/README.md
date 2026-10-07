# AbastecePyme Backend

API REST de AbastecePyme. Feature 1 es el catálogo de dependencias: registra proveedores, insumos y productos, y las dependencias entre ellos, y muestra la red resultante. Está organizada con Clean Architecture (FastAPI + SQLAlchemy).

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

Los errores siempre responden con `{error_code, message}`:

| Código HTTP | `error_code` | Cuándo |
|---|---|---|
| 404 | `ERR_ELEMENT_NOT_FOUND` | Uno de los extremos de la dependencia no existe |
| 409 | `ERR_DUPLICATE_ELEMENT` | Ya existe un elemento con ese nombre |
| 409 | `ERR_DUPLICATE_DEPENDENCY` | La relación ya estaba registrada |
| 400 | `ERR_SELF_DEPENDENCY` | Un elemento se requiere a sí mismo |
| 400 | `ERR_INVALID_DEPENDENCY_TYPE` | La combinación de tipos no tiene sentido de negocio |
| 422 | `ERR_VALIDATION` | JSON mal formado: campo faltante, tipo inválido, id que no es UUID, nombre vacío |

## Decisiones de diseño

**Dirección de las aristas: `A → B` significa "Para producir A necesito B".**
Ejemplo: `Pan → Harina → Molinos SA`. La frase invertida ("Para producir Harina necesito Pan") no tiene sentido, por eso el grafo es dirigido.
Consecuencia para F2: cuando falla un proveedor, el impacto se calcula recorriendo las aristas en sentido contrario, desde quienes lo necesitan. Esto debe resolverse en el modelo, por ejemplo con una adyacencia inversa, y no con condicionales.

**Reglas de tipos:**
- Un proveedor no depende de nada.
- Un insumo solo depende de proveedores.
- Un producto depende de insumos o de otros productos (productos intermedios).

**Identificador único:**
- El `id` es un UUID interno.
- El identificador de negocio es el **nombre**: único, sin distinguir mayúsculas y sin espacios al inicio o al final.

**Representación principal:**
- La clase propia `DependencyGraph` (`domain/graph/dependency_graph.py`) implementa una **lista de adyacencia**: `dict[id, list[id]]`.
- Se eligió porque el grafo es disperso (cada elemento depende de pocos otros) y los recorridos de F2 y F3 iteran vecinos. Ocupa O(V + E) en memoria y el acceso a los vecinos de un nodo es O(grado).
- La base SQL solo sirve para persistir. El grafo se reconstruye en memoria en cada consulta.

**Ciclos:**
- F1 rechaza la autodependencia directa (A → A).
- Los ciclos más largos (Pan → Masa madre → Pan) se registran. Detectarlos y alertar corresponde a F3.

## Pruebas de aceptación
1. Levante la API sobre una base vacía:
   ```bash
   set DATABASE_URL=sqlite:///./aceptacion.db
   uvicorn abastecepyme.presentation.main:app --app-dir src --port 8000
   ```
2. En otra terminal, ejecute:
   ```bash
   python scripts/aceptacion_f1.py
   ```

El script prueba el escenario normal, el grafo vacío, un nodo inexistente, una relación repetida, una autodependencia, un nombre repetido, datos inválidos, una relación con tipos inválidos y un ciclo. Para cada escenario imprime qué se esperaba, qué se obtuvo y si pasó o falló.
Antes de volver a ejecutarlo, borre `aceptacion.db`.
