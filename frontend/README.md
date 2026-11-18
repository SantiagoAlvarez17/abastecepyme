# AbastecePyme Frontend (Next.js + Tailwind + React Flow)

Interfaz web empresarial para **AbastecePyme**, organizada por roles de negocio:

- **Compras (`/compras`):** registro validado de elementos y dependencias, KPIs del catálogo, directorio filtrable con estado en red (`Conectado` / `Aislado`), diálogo de inspección y mapa interactivo de dependencias.
- **Tablero (`/tablero`):** simulación de indisponibilidad simultánea de varios elementos, resumen de productos detenidos o disponibles, niveles con rutas y fuentes, y resaltado de múltiples orígenes sobre el grafo. Los datos y cálculos se obtienen del backend mediante un BFS multifuente O(V + E).
- **Producción (`/produccion`):** consulta individual de impacto y requisitos por niveles con sus rutas completas.

## Requisitos
- Node.js 20+
- Backend corriendo en `http://localhost:8000` (configurable mediante `NEXT_PUBLIC_API_URL`)

## Instalación y ejecución
```bash
cd frontend
npm install
npm run dev
```
Se abre en [http://localhost:3000](http://localhost:3000).
