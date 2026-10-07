from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from abastecepyme.core.exceptions import BusinessException
from abastecepyme.presentation.routes.element_routes import router as element_router
from abastecepyme.presentation.routes.dependency_routes import router as dependency_router
from abastecepyme.presentation.routes.graph_routes import router as graph_router
from abastecepyme.infrastructure.database.models.base import Base
from abastecepyme.infrastructure.database.session import engine

# En un entorno productivo real usaríamos Alembic para las migraciones
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AbastecePyme API",
    description="Backend API estructurado bajo Clean Architecture",
    version="0.1.0"
)

# Prevención de CORS estricta (ajustar en prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Datos mal formados: misma forma de error que las excepciones de negocio
    details = [
        {
            "field": ".".join(str(part) for part in err["loc"][1:]),
            "message": str(err["msg"])
        }
        for err in exc.errors()
    ]
    summary = "; ".join(
        f"{d['field']}: {d['message']}" if d["field"] else d["message"] for d in details
    )
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "ERR_VALIDATION",
            "message": f"Datos mal formados. {summary}",
            "details": details
        }
    )

app.include_router(element_router)
app.include_router(dependency_router)
app.include_router(graph_router)