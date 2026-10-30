# AbastecePyme Frontend (Next.js + Tailwind + React Flow)

Interfaz web empresarial para **AbastecePyme**, organizada por roles de negocio:

- **Compras (`/compras`):** registro validado de elementos y dependencias, KPIs del catálogo, directorio filtrable con estado en red (`Conectado` / `Aislado`), diálogo de inspección y mapa interactivo de dependencias.
- **Producción (`/produccion`):** simulación de indisponibilidad (`mode=impact`) y consulta de requisitos (`mode=requirements`), métricas de alcance, desglose por niveles con ruta completa y frase de negocio, y resaltado en tiempo real sobre el grafo interactivo (React Flow + Dagre).

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
