"""
Programa: app/routers/catalogs.py
Objetivo: Exponer endpoints de solo lectura para consultar los catalogos maestros.
Fecha: 2026-11-24
Programador: <Tu Nombre>

Responsabilidad UNICA:
  - Consultar las tablas de catalogo (`document_types`, `species`) para apoyar
    la creacion de registros en `owners` y `pets`.
"""

from fastapi import APIRouter

from app.db_connection import get_connection
from app.errors import RESPUESTAS_ERROR

router = APIRouter(prefix="/catalogs", tags=["Catalogs"], responses=RESPUESTAS_ERROR)


@router.get("/document-types")
def listar_tipos_documento():
    """Devuelve el catalogo de tipos de documento validos para `owners`."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT doc_type_id, code, description "
                "FROM document_types ORDER BY doc_type_id"
            )
            return cursor.fetchall()


@router.get("/species")
def listar_especies():
    """Devuelve el catalogo de especies validas para `pets`."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT species_id, name FROM species ORDER BY species_id")
            return cursor.fetchall()