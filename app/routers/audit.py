"""
Programa: app/routers/audit.py
Objetivo: Exponer el endpoint de solo lectura para consultar el historial de auditoria.
Fecha: 2026-11-24
Programador: <Jonathan Cañola Salazar - Jorge Andrés García Mojica>

Responsabilidad UNICA:
- Consultar los registros de `audit_logs` (sin generar nuevos eventos de auditoria).
"""

from fastapi import APIRouter, Query

from app.db_connection import get_connection
from app.errors import RESPUESTAS_ERROR

router = APIRouter(prefix="/audit", tags=["Audit"], responses=RESPUESTAS_ERROR)


@router.get("")
def listar_auditoria(
    table_name: str | None = Query(
        default=None, description="Filtrar por tabla ('owners' o 'pets')"
    ),
    limit: int = Query(
        default=50, ge=1, le=200, description="Cantidad maxima de registros"
    ),
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