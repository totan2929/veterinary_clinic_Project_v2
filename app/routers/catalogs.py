"""
Programa: app/routers/catalogs.py
Objetivo: Exponer endpoints de solo lectura para catalogos maestros y registros de auditoria.
Fecha: 2026-11-22
Programador: <Tu Nombre>

Responsabilidad UNICA:
  - Consultar tablas de catalogo (`document_types`, `species`) para apoyar las pruebas en /docs.
  - Consultar el historial de cambios en `audit_logs` (sin generar nuevos eventos de auditoria).
"""

from fastapi import APIRouter, Query

from app.db_connection import get_connection
from app.errors import RESPUESTAS_ERROR

router = APIRouter(tags=["Catalogs & Audit"], responses=RESPUESTAS_ERROR)


@router.get("/catalogs/document-types")
def listar_tipos_documento():
    """Devuelve el catalogo de tipos de documento validos para `owners`."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT doc_type_id, code, description FROM document_types ORDER BY doc_type_id")
            return cursor.fetchall()


@router.get("/catalogs/species")
def listar_especies():
    """Devuelve el catalogo de especies validas para `pets`."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT species_id, name FROM species ORDER BY species_id")
            return cursor.fetchall()


@router.get("/audit")
def listar_auditoria(
    table_name: str | None = Query(default=None, description="Filtrar por tabla ('owners' o 'pets')"),
    limit: int = Query(default=50, ge=1, le=200, description="Cantidad maxima de registros"),
):
    """Devuelve los eventos mas recientes registrados en `audit_logs`."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            if table_name:
                cursor.execute(
                    "SELECT audit_id, table_name, operation, record_id, old_data, new_data, "
                    "performed_by, created_at FROM audit_logs "
                    "WHERE table_name = %s ORDER BY audit_id DESC LIMIT %s",
                    (table_name, limit),
                )
            else:
                cursor.execute(
                    "SELECT audit_id, table_name, operation, record_id, old_data, new_data, "
                    "performed_by, created_at FROM audit_logs "
                    "ORDER BY audit_id DESC LIMIT %s",
                    (limit,),
                )
            return cursor.fetchall()