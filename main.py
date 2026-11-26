"""
Programa: main.py
Objetivo: Punto de entrada de la API REST Veterinary Clinic (FastAPI + MySQL).
Fecha: 2026-11-24
Programador: <Jonathan Cañola Salazar - Jorge Andrés García Mojica>

Responsabilidad UNICA:
  - Crear la instancia principal de FastAPI con su metadato OpenAPI.
  - Registrar los manejadores globales de errores (app/errors.py).
  - Incluir los routers de la aplicacion (owners, pets, catalogs, audit).

Ejecucion desde la raiz del proyecto:
  Linux/Omarchy: ./.venv/bin/python -m uvicorn main:app --reload
  Windows:       .\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload
Documentacion interactiva:
  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from app.errors import registrar_manejadores
from app.routers import audit, catalogs, owners, pets

app = FastAPI(
    title="Veterinary Clinic API",
    description="API REST en Python (FastAPI + MySQL) para la gestion de duenos, mascotas y auditoria.",
    version="1.0.0",
)

# Registro global de manejadores de error (MySQLError, HTTPException, Pydantic, Exception)
registrar_manejadores(app)

# Inclusion de routers por recurso
app.include_router(owners.router)
app.include_router(pets.router)
app.include_router(catalogs.router)
app.include_router(audit.router)


@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz para verificar que la API esta activa."""
    return {
        "message": "Veterinary Clinic API - Programacion V",
        "version": "1.0.0",
        "docs": "/docs",
        "autors-devs": ["Jonathan Cañola Salazar", "Jorge Andrés García Mojica"]
    }