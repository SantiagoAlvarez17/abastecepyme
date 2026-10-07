FROM python:3.1-slim

# Instalar dependencias del sistema y el driver ODBC 17 para SQL Server
RUN apt-get update && apt-get install -y curl apt-transport-https gnupg2 g++ \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar hatch
RUN pip install hatch

# Copiar archivos
COPY . .

# Exponer el puerto
EXPOSE 8000

# Usar PYTHONPATH para que Python encuentre el paquete 'abastecepyme' en 'src'
ENV PYTHONPATH=/app/src

# Arrancar el servidor
CMD ["hatch", "run", "uvicorn", "abastecepyme.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
