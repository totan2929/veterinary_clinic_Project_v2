"""
Programa: app/auditoria.py
Objetivo: Registrar en `audit_logs` quien, cuando y que cambio en cada escritura.
Fecha: 2026-11-24
Programador: <Tu Nombre>

Responsabilidad UNICA:
  - Identificar al usuario que realiza la peticion (encabezado X-Usuario o IP).
  - Insertar el evento de auditoria usando el mismo cursor/transaccion del cambio
    principal, garantizando atomicidad (si el cambio falla, se revierte todo).
"""

import json

from fastapi import Request

_CODIGOS_OPERACION = {
    "INSERT": "I",
    "UPDATE": "U",
    "DELETE": "D",
}


def usuario_desde(request: Request) -> str:
    """Obtiene el identificador del autor del cambio desde la peticion HTTP."""
    return request.headers.get("X-Usuario") or (
        request.client.host if request.client else "desconocido"
    )


def registrar_auditoria(
    cursor,
    table_name: str,
    operacion: str,
    record_id: int,
    anteriores: dict | None,
    nuevos: dict | None,
    usuario: str,
) -> None:
    """Inserta un registro de auditoria en `audit_logs` dentro de la transaccion activa."""
    try:
        codigo_operacion = _CODIGOS_OPERACION[operacion]
    except KeyError as error:
        raise ValueError(f"Operacion de auditoria no valida: {operacion}") from error

    cursor.execute(
        "INSERT INTO audit_logs "
        "(table_name, operation, record_id, old_data, new_data, performed_by) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (
            table_name,
            codigo_operacion,
            record_id,
            json.dumps(anteriores, default=str) if anteriores else None,
            json.dumps(nuevos, default=str) if nuevos else None,
            usuario,
        ),
    )