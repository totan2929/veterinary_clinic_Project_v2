"""
Programa: app/errors.py
Objetivo: Centralizar el manejo global y uniforme de errores HTTP y de base de datos.
Fecha: 2026-11-24
Programador: <Tu Nombre>

Responsabilidad UNICA:
  - Capturar excepciones de FastAPI, Pydantic, MySQL y errores inesperados.
  - Traducirlos a una respuesta JSON uniforme y documentarlos en OpenAPI (/docs).
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

ER_DUP_ENTRY = 1062
ER_ROW_IS_REFERENCED = 1451
ER_NO_REFERENCED_ROW = 1452

_TIPOS = {
    400: "solicitud_invalida",
    404: "no_encontrado",
    409: "conflicto",
    422: "validacion",
    500: "error_interno",
}


class ErrorDetalle(BaseModel):
    """Estructura del detalle de error devuelto al cliente."""

    codigo: int
    tipo: str
    mensaje: str
    detalles: list | None = None


class ErrorRespuesta(BaseModel):
    """Envoltura JSON unica para todas las respuestas de error de la API."""

    error: ErrorDetalle


RESPUESTAS_ERROR = {
    400: {"model": ErrorRespuesta, "description": "Solicitud invalida o referencia inexistente."},
    404: {"model": ErrorRespuesta, "description": "Recurso no encontrado."},
    409: {"model": ErrorRespuesta, "description": "Conflicto: dato duplicado o registro en uso."},
    422: {"model": ErrorRespuesta, "description": "Datos no validos (validacion de Pydantic)."},
    500: {"model": ErrorRespuesta, "description": "Error interno o de base de datos."},
}


def _cuerpo(codigo: int, mensaje: str, detalles: list | None = None) -> dict:
    """Construye el diccionario estandar de error."""
    error = {"codigo": codigo, "tipo": _TIPOS.get(codigo, "error"), "mensaje": mensaje}
    if detalles:
        error["detalles"] = detalles
    return {"error": error}


async def _manejar_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Traduce excepciones HTTP de negocio (400, 404, 409) al formato uniforme."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_cuerpo(exc.status_code, str(exc.detail)),
        headers=getattr(exc, "headers", None),
    )


async def _manejar_validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Traduce errores de validacion de Pydantic a HTTP 422 con detalle por campo."""
    detalles = [
        {
            "campo": ".".join(str(parte) for parte in error["loc"] if parte != "body"),
            "mensaje": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_cuerpo(422, "Los datos enviados no son validos.", detalles),
    )


async def _manejar_mysql(request: Request, exc: MySQLError) -> JSONResponse:
    """Traduce errores especificos de MySQL a codigos HTTP semanticos."""
    if exc.errno == ER_DUP_ENTRY:
        return JSONResponse(
            status_code=409,
            content=_cuerpo(409, "Ya existe un registro con ese valor unico (documento, correo o chip)."),
        )
    if exc.errno == ER_NO_REFERENCED_ROW:
        return JSONResponse(
            status_code=400,
            content=_cuerpo(400, "Referencia invalida: uno de los IDs relacionados no existe."),
        )
    if exc.errno == ER_ROW_IS_REFERENCED:
        return JSONResponse(
            status_code=409,
            content=_cuerpo(409, "No se puede eliminar el registro porque tiene datos asociados."),
        )
    return JSONResponse(
        status_code=500,
        content=_cuerpo(500, "Error al acceder a la base de datos."),
    )


async def _manejar_inesperado(request: Request, exc: Exception) -> JSONResponse:
    """Captura cualquier excepcion no controlada y responde HTTP 500 uniforme."""
    return JSONResponse(
        status_code=500,
        content=_cuerpo(500, "Error interno inesperado del servidor."),
    )


def registrar_manejadores(app: FastAPI) -> None:
    """Registra todos los manejadores globales de excepciones en la aplicacion FastAPI."""
    app.add_exception_handler(StarletteHTTPException, _manejar_http_exception)
    app.add_exception_handler(RequestValidationError, _manejar_validacion)
    app.add_exception_handler(MySQLError, _manejar_mysql)
    app.add_exception_handler(Exception, _manejar_inesperado)