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
- **Representación:** listas de adyacencia propias (`DependencyGraph`), una de salida y otra inversa, sin librerías de grafos.
- **Interfaz:** la red se dibuja con Graphviz a partir de lo que devuelve `GET /graph`. La interfaz no calcula nada del grafo por su cuenta.


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

El script prueba el escenario normal, el grafo vacío, un nodo inexistente, una relación no registrada, una relación repetida, una autodependencia, un nombre repetido, datos inválidos, una relación con tipos inválidos y un ciclo. Para cada escenario imprime qué se esperaba, qué se obtuvo y si pasó o falló.
Antes de volver a ejecutarlo, borre `aceptacion.db`.

| GET | `/impact/{element_id}` | Qué se afecta si el elemento no está disponible (`mode=impact`, por defecto) |
| GET | `/impact/{element_id}?mode=requirements` | Qué necesita el elemento para producirse |

## Análisis de impacto (Feature 2)

**¿Qué significa "alcanzar" en este negocio?** Un elemento Y es alcanzado desde X cuando existe una cadena de relaciones "Para producir A necesito B" que los une, en el sentido de la consulta. El nivel 1 es la relación directa, el nivel 2 es lo que depende de lo anterior, y así sucesivamente. Cada elemento se informa una sola vez, con su nivel mínimo.

**Dos consultas con un solo recorrido** (`GET /impact/{element_id}`):

| `mode` | Pregunta de negocio | Sentido del recorrido |
|---|---|---|
| `impact` (por defecto) | Si este proveedor/insumo falla, ¿qué productos y procesos se afectan? | Contra las flechas: de B hacia quienes lo requieren (índice `_required_by`) |
| `requirements` | Para producir este producto, ¿qué necesito, hasta llegar a los proveedores? | Con las flechas: de A hacia lo que requiere (índice `_requires`) |

La dirección la resuelve el modelo con sus dos índices, no con condicionales en el recorrido: `DependencyGraph.reach(origen, reverse=...)` solo elige cuál índice seguir.

**Algoritmo:** recorrido en anchura (BFS) propio, con una cola y un conjunto de visitados (`reach` en `domain/graph/dependency_graph.py`). Complejidad O(V + E) en tiempo y O(V) en memoria. Como el conjunto de visitados evita repetir elementos, el recorrido termina aunque el catálogo contenga ciclos (F1 permite registrarlos; su detección y alerta son de F3). Se eligió BFS porque entrega los elementos por niveles, lo que permite distinguir la afectación directa de la afectación en cadena.

**Resultado.** Los elementos visitados se agrupan por nivel y cada uno trae su ruta desde el origen y la frase "Para producir X necesito Y" de la relación recorrida. Se distinguen tres casos sobre un elemento que existe, más el caso de que no exista:

| Caso | Respuesta | `outcome` |
|---|---|---|
| El elemento no existe (o está inactivo) | 404 `ERR_ELEMENT_NOT_FOUND` | — |
| No tiene ninguna dependencia registrada | 200 | `isolated` |
| Tiene relaciones, pero ninguna en el sentido consultado (p. ej., nadie necesita un producto final) | 200 | `no_reach` |
| Alcanza al menos un elemento | 200 | `chain` |

Ejemplo abreviado de `GET /impact/{id de Molinos del Valle}` con los datos de ejemplo:

```json
{
  "mode": "impact",
  "outcome": "chain",
  "summary": "Si “Molinos del Valle” no está disponible, se afectan 6 elementos en 4 niveles de la cadena.",
  "affected_count": 6,
  "max_level": 4,
  "levels": [
    {"level": 1, "label": "Afectación directa", "elements": ["Harina de trigo"]},
    {"level": 2, "label": "Afectación en cadena · nivel 2", "elements": ["Masa madre", "Torta de vainilla"]},
    {"level": 3, "label": "Afectación en cadena · nivel 3", "elements": ["Pan", "Croissant"]},
    {"level": 4, "label": "Afectación en cadena · nivel 4", "elements": ["Combo desayuno"]}
  ]
}
```

(En la respuesta real, cada elemento es un objeto con `id`, `name`, `element_type`, `level`, `via_id`, `reason` y `path`.)

Para la Feature 2, con la API sobre otra base vacía (`aceptacion.db` borrada), ejecute `python scripts/aceptacion_f2.py`. Prueba la falla de un proveedor y de un insumo, la consulta hacia un producto, un elemento aislado, uno sin alcance, un elemento inexistente, datos inválidos y un ciclo.
