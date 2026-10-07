# Bitácora de uso de IA — Feature 1: Catálogo de dependencias

- **Herramienta:** Claude Code (app de escritorio). Modelos: Claude Sonnet 5.5 en la interpretación inicial y Claude Opus 5.5 en el resto.
- **Fecha de la sesión:** 2026-10-06
- **Punto de partida:** avance compartido por un compañero (backend en FastAPI con Clean Architecture y frontend en Next.js). Todos los cambios se hicieron sobre una **copia**; el avance original no se modificó.

> **Nota para el equipo:** si el avance inicial también se hizo con ayuda de IA (la carpeta `frontend/` incluye un `AGENTS.md`, que suelen usar los asistentes de código), quien lo hizo debe agregar sus propias filas a esta tabla.

## Registro de decisiones

| Decisión o pieza | Herramienta/objetivo de IA | Propuesta recibida | Acepté o rechacé y por qué | Cómo la verifiqué |
|---|---|---|---|---|
| Interpretación del brief y la guía | Claude Code: resumir los requisitos de F1 sin escribir código | Lista de requisitos, modelo de grafo (nodos, aristas dirigidas, lista de adyacencia), casos de aceptación y dudas abiertas | Acepté como punto de partida. Las decisiones de modelado quedaron para el equipo | Lectura cruzada con el brief (sección F1) y la guía (reglas no negociables) |
| Revisión del avance del compañero | Claude Code: revisar el código contra los requisitos de F1 | Encontró que se aceptaban relaciones repetidas (`merge`) y autodependencias, que el id repetido no se podía probar, que faltaba `GET` de la red, que no había grafo propio, que el frontend esperaba nombres de campo distintos a los de la API y que faltaban el script, `requirements.txt` y Python 3.12 | Acepté. Los hallazgos coincidían con los requisitos del brief | Prueba ejecutada contra la API original: **7/13 casos pasaron**, lo que confirmó los errores |
| Identificador único de los elementos | Pedir una alternativa que se pudiera probar | Hacer único el **nombre** (sin distinguir mayúsculas ni espacios) y mantener el UUID como id interno. La alternativa era un código legible tipo `INS-HARINA` | Acepté **de forma provisional**: es el cambio más pequeño sobre el modelo existente. **Pendiente de confirmar en equipo** | Escenario "Identificador repetido" del script (`'  harina '` → 409) |
| Rechazo de relaciones repetidas | Corregir el error | Reemplazar `db.merge` por `db.add`, agregar `exists()` al repositorio y responder 409 `ERR_DUPLICATE_DEPENDENCY` | Acepté. Lo exige el brief ("validar relaciones repetidas") | Escenario "Relación repetida" (409) |
| Rechazo de autodependencia | Corregir el error | Responder 400 `ERR_SELF_DEPENDENCY` con el nombre del elemento en el mensaje | Acepté. "Para producir Pan necesito Pan" no tiene sentido de negocio | Escenario "Autodependencia" (400) y mensaje revisado en la interfaz |
| Representación del grafo | Crear el grafo propio | Clase `DependencyGraph` con lista de adyacencia (`dict[id, list[id]]`), reconstruida desde la base en cada consulta | Acepté. Rechacé usar NetworkX, porque la guía exige representación y algoritmos propios. La lista de adyacencia conviene porque el grafo es disperso y F2/F3 recorren vecinos | `GET /graph` devuelve la adyacencia esperada (`Pan → [Masa madre]`) en el script |
| Dirección de las aristas | Revisar la dirección del compañero | Mantener `A → B` = "Para producir A necesito B". Advirtió que F2 deberá recorrer las aristas en sentido inverso | Acepté la dirección. **Queda para F2** decidir cómo modelar el recorrido inverso (adyacencia inversa), sin resolverlo con condicionales | Frases "Para producir ___ necesito ___" en la interfaz y el script; la frase invertida no tiene sentido |
| Ciclos en F1 | Decidir si rechazarlos al registrar | Registrar los ciclos largos y dejar su detección a F3; rechazar solo A → A | Acepté. F3 pide detectar y reportar ciclos, lo que supone que pueden existir en los datos. Descarté rechazarlos en F1 | Escenario "Ciclo" (201) y ciclo Pan ↔ Masa madre visible en el grafo |
| Formato de errores de validación | Unificar las respuestas de error | Manejador de `RequestValidationError` que devuelve `{error_code: ERR_VALIDATION, message, details}` | Acepté. La interfaz necesita un `message` legible en todos los errores | 4 escenarios de "Dato inválido" (422 con `message`) |
| Script de aceptación | Escribir las pruebas que pide la guía | Script en Python que usa solo `urllib` contra la API levantada con uvicorn e imprime escenario, lo esperado, lo obtenido y PASA/FALLA | Acepté. Rechacé pytest y httpx porque la guía pide pruebas sin frameworks adicionales | Ejecución contra la API real: **24/24 escenarios pasaron** |
| Nombres de campo en el frontend Next.js | Corregir el desajuste entre `snake_case` y `camelCase` | Funciones `toElement` y `toDependency` en los repositorios de la API | Acepté el cambio, pero **no está verificado**: en el equipo de la sesión no había Node.js para compilarlo | **Pendiente:** compilar y probar si se mantiene Next.js |
| Interfaz mínima | Elegir tecnología y construirla | Streamlit consumiendo la API real. El grafo se dibuja con Graphviz desde `GET /graph`, sin calcular nada en el frontend | Acepté Streamlit (decisión del equipo): usa el mismo Python que el backend. Rechacé NetworkX para dibujar porque no era necesario | Prueba automática con `streamlit.testing` contra la API (**14/14 comprobaciones**) y revisión visual en el navegador |
| Entorno: Python y dependencias | Instalar y fijar versiones | Instalar Python 3.13 (el archivo descargado era código fuente `.tar.xz`, no un instalador), `requirements.txt` con versiones fijas y `requires-python >= 3.12` | Acepté. Cumple "Python 3.12+" y permite reproducir el proyecto | `python --version` y ejecución completa de la API y la interfaz en un entorno virtual nuevo |
| Docker y SQL Server | Revisar el `docker-compose` del compañero | Señaló que probablemente no arranca (falta `pyodbc`, Python 3.10, contraseña escrita en el archivo) y sugirió quitarlo, ya que SQLite alcanza | **Pendiente de decidir en equipo.** No se modificó | No verificado: no se ejecutó Docker |

## Qué debe poder explicar el equipo (auditoría)

La guía dice que el código que no se puede explicar, trazar y verificar cuenta como no entregado. Antes del pitch, cada integrante debería poder responder:

1. **¿Por qué la arista va de producto a insumo?** Porque se lee "Para producir A necesito B". ¿Qué implica eso para el análisis de impacto de F2?
2. **¿Cómo está guardado el grafo en memoria?** Ver `backend/src/abastecepyme/domain/graph/dependency_graph.py`. ¿Cuánto cuesta en memoria y en consultas de vecinos?
3. **¿En qué orden se valida una dependencia?** Existencia → autodependencia → reglas de tipo → duplicado. Ver `register_dependency.py`.
4. **¿Por qué F1 acepta ciclos largos pero rechaza A → A?**
5. **¿Qué devuelve `GET /graph`** con el catálogo vacío y con datos?

**Pendiente recomendado:** hacer una **traza manual** en papel con el ejemplo Molinos SA → Harina / Levadura → Masa madre → Pan, y compararla con la salida de `GET /graph`. La guía la menciona como forma de verificación y no se hizo en esta sesión.
