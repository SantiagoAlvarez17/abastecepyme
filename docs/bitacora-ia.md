# Bitácora de uso de IA — Feature 1: Catálogo de dependencias

La bitácora está organizada por sesión de trabajo. Cada sección indica el commit con el que entró al repositorio, para que cada fila se pueda rastrear hasta su autor.

> **Nota para el equipo:** el andamiaje inicial (`be6e481`, backend en Clean Architecture y frontend en Next.js) también se hizo con ayuda de IA (la carpeta `frontend/` incluía un `AGENTS.md`). Su autor debe completar las filas marcadas como **[Completar]** en la sesión 3.

## Sesión 1 — Revisión e integración de F1 (commit `5952757`, DioGZ)

- **Herramienta:** Claude Code (app de escritorio). Modelos: Claude Sonnet 5.5 en la interpretación inicial y Claude Opus 5.5 en el resto.
- **Fecha:** 2026-10-06
- **Punto de partida:** avance compartido por un compañero (backend en FastAPI con Clean Architecture y frontend en Next.js). Todos los cambios se hicieron sobre una **copia**; el avance original no se modificó.

| Decisión o pieza | Herramienta/objetivo de IA | Propuesta recibida | Acepté o rechacé y por qué | Cómo la verifiqué |
|---|---|---|---|---|
| Interpretación del brief y la guía | Claude Code: resumir los requisitos de F1 sin escribir código | Lista de requisitos, modelo de grafo (nodos, aristas dirigidas, lista de adyacencia), casos de aceptación y dudas abiertas | Acepté como punto de partida. Las decisiones de modelado quedaron para el equipo | Lectura cruzada con el brief (sección F1) y la guía (reglas no negociables) |
| Revisión del avance del compañero | Claude Code: revisar el código contra los requisitos de F1 | Encontró que se aceptaban relaciones repetidas (`merge`) y autodependencias, que el id repetido no se podía probar, que faltaba `GET` de la red, que no había grafo propio, que el frontend esperaba nombres de campo distintos a los de la API y que faltaban el script, `requirements.txt` y Python 3.12 | Acepté. Los hallazgos coincidían con los requisitos del brief | Prueba ejecutada contra la API original: **7/13 casos pasaron**, lo que confirmó los errores |
| Identificador único de los elementos | Pedir una alternativa que se pudiera probar | Hacer único el **nombre** (sin distinguir mayúsculas ni espacios) y mantener el UUID como id interno. La alternativa era un código legible tipo `INS-HARINA` | Acepté **de forma provisional**: es el cambio más pequeño sobre el modelo existente. **Pendiente de confirmar en equipo** | Escenario "Identificador repetido" del script (`'  harina '` → 409) |
| Rechazo de relaciones repetidas | Corregir el error | Reemplazar `db.merge` por `db.add`, agregar `exists()` al repositorio y responder 409 `ERR_DUPLICATE_DEPENDENCY` | Acepté. Lo exige el brief ("validar relaciones repetidas") | Escenario "Relación repetida" (409) |
| Rechazo de autodependencia | Corregir el error | Responder 400 `ERR_SELF_DEPENDENCY` con el nombre del elemento en el mensaje | Acepté. "Para producir Pan necesito Pan" no tiene sentido de negocio | Escenario "Autodependencia" (400) y mensaje revisado en la interfaz |
| Representación del grafo | Crear el grafo propio | Clase `DependencyGraph` con lista de adyacencia (`dict[id, list[id]]`), reconstruida desde la base en cada consulta | Acepté. Rechacé usar NetworkX, porque la guía exige representación y algoritmos propios. La lista de adyacencia conviene porque el grafo es disperso y F2/F3 recorren vecinos. *(En la sesión 3 se reemplazó por la versión con adyacencia inversa)* | `GET /graph` devuelve la adyacencia esperada (`Pan → [Masa madre]`) en el script |
| Dirección de las aristas | Revisar la dirección del compañero | Mantener `A → B` = "Para producir A necesito B". Advirtió que F2 deberá recorrer las aristas en sentido inverso | Acepté la dirección. El recorrido inverso quedó resuelto en la sesión 3 con una adyacencia inversa, sin condicionales | Frases "Para producir ___ necesito ___" en la interfaz y el script; la frase invertida no tiene sentido |
| Ciclos en F1 | Decidir si rechazarlos al registrar | Registrar los ciclos largos y dejar su detección a F3; rechazar solo A → A | Acepté. F3 pide detectar y reportar ciclos, lo que supone que pueden existir en los datos. Descarté rechazarlos en F1 | Escenario "Ciclo" (201) y ciclo Pan ↔ Masa madre visible en el grafo |
| Formato de errores de validación | Unificar las respuestas de error | Manejador de `RequestValidationError` que devuelve `{error_code: ERR_VALIDATION, message, details}` | Acepté. La interfaz necesita un `message` legible en todos los errores | 4 escenarios de "Dato inválido" (422 con `message`) |
| Script de aceptación | Escribir las pruebas que pide la guía | Script en Python que usa solo `urllib` contra la API levantada con uvicorn e imprime escenario, lo esperado, lo obtenido y PASA/FALLA | Acepté. Usé solo la biblioteca estándar para que el script no dependa de nada más; la guía pide este script y no exige `pytest` | Ejecución contra la API real: **24/24 escenarios pasaron** |
| Nombres de campo en el frontend Next.js | Corregir el desajuste entre `snake_case` y `camelCase` | Funciones `toElement` y `toDependency` en los repositorios de la API | Acepté el cambio, pero no se pudo verificar: en el equipo de la sesión no había Node.js para compilarlo. *(En la sesión 3 se eliminó el frontend Next.js)* | No verificado |
| Interfaz mínima | Elegir tecnología y construirla | Streamlit consumiendo la API real. El grafo se dibuja con Graphviz desde `GET /graph`, sin calcular nada en el frontend | Acepté Streamlit (decisión del equipo): usa el mismo Python que el backend. Rechacé NetworkX para dibujar porque no era necesario | Prueba automática con `streamlit.testing` contra la API (**14/14 comprobaciones**) y revisión visual en el navegador |
| Entorno: Python y dependencias | Instalar y fijar versiones | Instalar Python 3.13 (el archivo descargado era código fuente `.tar.xz`, no un instalador), `requirements.txt` con versiones fijas y `requires-python >= 3.12` | Acepté. Cumple "Python 3.12+" y permite reproducir el proyecto | `python --version` y ejecución completa de la API y la interfaz en un entorno virtual nuevo |
| Docker y SQL Server | Revisar el `docker-compose` del compañero | Señaló que probablemente no arranca (falta `pyodbc`, Python 3.10, contraseña escrita en el archivo) y sugirió quitarlo, ya que SQLite alcanza | Quedó pendiente de decidir en equipo. *(En la sesión 3 se eliminó)* | No verificado: no se ejecutó Docker |

## Sesión 2 — Puesta en marcha y datos de ejemplo (commit `2e7d01f`, cuenta SantiagoAlvarez17)

| Decisión o pieza | Herramienta/objetivo de IA | Propuesta recibida | Acepté o rechacé y por qué | Cómo la verifiqué |
|---|---|---|---|---|
| Puesta en marcha del proyecto en mi equipo | Claude (chat): diagnosticar errores de ejecución | Errores `ModuleNotFoundError`, política de ejecución de PowerShell e intérprete de VS Code; propuso instalar con `pip install -e .`, usar un entorno virtual y seleccionar el intérprete correcto | Acepté | El backend arrancó, `/docs` abrió y el frontend cargó en `localhost:3000` |
| Revisión del proyecto contra el brief y la guía | Claude (chat): comparar el código con los requisitos | Señaló la falta de grafo propio, de validación de duplicados y el desajuste de nombres de campo (`snake_case` y `camelCase`) | Acepté los hallazgos; coinciden con los de **[Completar: nombre del compañero]** | Lectura del brief y de su rama |
| Código propuesto por Claude: validaciones, ciclos, `pytest` e interfaz en Next.js | Claude (chat): generar código para la Feature 1 | Rechazo de ciclos al registrar, pruebas con `pytest` y una interfaz en Next.js | En esta sesión no lo integré en `feature/datos-ejemplo`, porque la rama del equipo ya traía una versión y F1 solo rechaza A → A (los ciclos son de F3). *(El grafo con adyacencia inversa y las pruebas `pytest` se integraron después, en la sesión 3; el rechazo de ciclos y Next.js se descartaron)* | **[Completar: qué probé yo]** |
| Datos sintéticos de ejemplo | Claude (chat): proponer un escenario y un script | Script `cargar_datos_ejemplo.py` con una panadería ficticia (18 elementos, 22 dependencias) | Acepté | Ejecutado contra la API real en la sesión 3: 18 elementos y 22 dependencias creados; `GET /graph` devolvió 18 nodos y 22 aristas. **[Completar: segunda ejecución para comprobar que no duplica]** |

## Sesión 3 — Resolución del PR #1 y cierre de F1 (commit de merge `9158ddc` y siguiente, Andrés David Arias Gómez)

- **Herramienta:** Claude Code (extensión de VS Code), modelo Claude Opus 5.5.
- **Fecha:** 2026-10-07
- **Punto de partida:** el PR #1 (`AndresArias` → `feature/datos-ejemplo`) tenía conflictos en 14 archivos.

| Decisión o pieza | Herramienta/objetivo de IA | Propuesta recibida | Acepté o rechacé y por qué | Cómo la verifiqué |
|---|---|---|---|---|
| Andamiaje Clean Architecture de F1 (`be6e481`) | **[Completar]** | **[Completar]** | **[Completar]** | **[Completar]** |
| Grafo con adyacencia inversa, detección de ciclos y pruebas `pytest` (`1be0647`, `7732848`) | **[Completar]** | **[Completar]** | **[Completar]** | **[Completar]** |
| Diagnóstico de los conflictos del PR #1 | Claude Code: analizar los conflictos sin modificar la rama | Simular el merge en memoria (`git merge-tree`). Encontró dos implementaciones paralelas de F1 con contratos distintos: nombres de códigos de error, forma de `GET /graph` y nombre del caso de uso | Acepté el diagnóstico. Rechacé su primera hipótesis (historias sin ancestro común) porque `git merge-base` sí encontró uno | Simulación del merge y revisión archivo por archivo de los 14 conflictos |
| Criterio para resolver el merge | Claude Code: proponer una regla de resolución | Mantener el contrato público de la rama destino, porque ya lo consumen la interfaz Streamlit, los scripts y el README, y conservar la lógica interna de mi rama: adyacencia inversa, `has_path`, manejo de `IntegrityError` y pruebas. `GET /graph` queda como unión: `direction`, `adjacency` y aristas con `description` | Acepté. Cambiar el contrato habría roto `ui/app.py`, que lee `adjacency`, y el script de aceptación | `pytest` 25/25 y script de aceptación contra la API real |
| Conflictos semánticos que git no marca | Claude Code: revisar el código ya fusionado | Doble validación de autodependencia con firmas de excepción incompatibles; métodos abstractos `exists` y `get_all` duplicados en `DependencyRepository`; 26 archivos `.pyc` que el merge volvía a versionar; `Dockerfile` con `python:3.1-slim` | Acepté y corregí los cuatro | Lectura del resultado del merge y ejecución de `pytest` |
| Rechazo de ciclos en F1 | Claude Code: resolver la diferencia entre ramas | Primero conservó el rechazo de ciclos de mi rama; el script de aceptación falló (**23/24**) porque el equipo había decidido registrarlos | Lo descarté y seguí la decisión del equipo (sesión 1, fila "Ciclos en F1"). `would_create_cycle` y `has_path` se quedan en el grafo para F3 | Script de aceptación **24/24**; las pruebas de ciclos ahora comprueban que el ciclo se registra |
| Pruebas `pytest` | Claude Code: decidir si se conservan | La guía no exige `pytest` ni lo prohíbe; el entregable obligatorio es el script. Propuso dejarlas como apoyo, con `requirements-dev.txt` y `pythonpath` configurado en `pyproject.toml` | Acepté: prueban el grafo y los casos de uso sin base de datos | `python -m pytest tests`: **25/25** |
| Frontend Next.js y Docker | Claude Code: revisar el repositorio contra la guía | Ninguno de los dos estaba verificado (Next.js no se compiló, Docker no se ejecutó, la contraseña de SQL Server estaba en el archivo) y la interfaz de Streamlit ya cubre el requisito | Acepté eliminarlos para que el repositorio solo contenga lo que funciona. **Informar al equipo en el PR** | Interfaz Streamlit probada con `streamlit.testing` contra la API con datos de ejemplo: sin excepciones, 18 elementos, 22 dependencias y el grafo dibujado |
| Escenario "relación inexistente" | Claude Code: revisar el script contra la guía | Faltaba el escenario de relación inexistente que pide la guía. Propuso comprobar que "Para producir Pan necesito Molinos SA" no aparece como arista directa, aunque sí exista un camino indirecto | Acepté | Script de aceptación **25/25** |

## Qué debe poder explicar el equipo (auditoría)

La guía dice que el código que no se puede explicar, trazar y verificar cuenta como no entregado. Antes del pitch, cada integrante debería poder responder:

1. **¿Por qué la arista va de producto a insumo?** Porque se lee "Para producir A necesito B". ¿Qué implica eso para el análisis de impacto de F2?
2. **¿Cómo está guardado el grafo en memoria?** Ver `backend/src/abastecepyme/domain/graph/dependency_graph.py`. ¿Para qué sirve el segundo índice (`_required_by`)? ¿Cuánto cuesta en memoria y en consultas de vecinos?
3. **¿En qué orden se valida una dependencia?** Existencia → autodependencia → reglas de tipo → duplicado. Ver `register_dependency.py`.
4. **¿Por qué F1 acepta ciclos largos pero rechaza A → A?** ¿Qué hace `would_create_cycle` y por qué F1 no lo usa?
5. **¿Qué devuelve `GET /graph`** con el catálogo vacío y con datos?

**Pendiente recomendado:** hacer una **traza manual** en papel con el ejemplo Molinos SA → Harina / Levadura → Masa madre → Pan, y compararla con la salida de `GET /graph`. La guía la menciona como forma de verificación y todavía no se ha hecho.
