"""
Programa: app/routers/owners.py
Objetivo: Exponer los endpoints HTTP (CRUD + PATCH + mascotas por dueno) del recurso `owners`.
Fecha: 2026-11-22
Programador: <Tu Nombre>

Responsabilidad UNICA:
  - Recibir peticiones HTTP sobre /owners (datos ya validados por Pydantic).
  - Ejecutar sentencias SQL parametrizadas (%s) usando conexiones del pool.
  - Registrar cada escritura (INSERT, UPDATE, DELETE) en `audit_logs` dentro de la misma transaccion.
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.auditoria import registrar_auditoria, usuario_desde
from app.db_connection import get_connection
from app.errors import RESPUESTAS_ERROR
from app.schemas.owner import OwnerCreate, OwnerPatch, OwnerResponse, OwnerUpdate

router = APIRouter(prefix="/owners", tags=["Owners"], responses=RESPUESTAS_ERROR)

_COLUMNAS = (
    "owner_id, doc_type_id, doc_number, first_name, last_name, birth_date, "
    "address, phone, email, is_active, created_at"
)


def _buscar_por_id(cursor, owner_id: int) -> dict | None:
    """Consulta un dueno por su llave primaria `owner_id`.

    Args:
        cursor: Cursor MySQL activo (dictionary=True).
        owner_id (int): Identificador del dueno.

    Returns:
        dict | None: Registro encontrado o None si no existe.
    """
    cursor.execute(f"SELECT {_COLUMNAS} FROM owners WHERE owner_id = %s", (owner_id,))
    return cursor.fetchone()


def _exigir_existencia(cursor, owner_id: int) -> dict:
    """Devuelve el dueno solicitado o lanza HTTP 404 si no existe."""
    owner = _buscar_por_id(cursor, owner_id)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un dueno con el ID {owner_id}.",
        )
    return owner


@router.post("", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
def crear_owner(owner: OwnerCreate, request: Request):
    """Crea un dueno nuevo y registra el evento en `audit_logs`."""
    sql = (
        "INSERT INTO owners "
        "(doc_type_id, doc_number, first_name, last_name, birth_date, address, phone, email, is_active) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    valores = (
        owner.doc_type_id,
        owner.doc_number,
        owner.first_name,
        owner.last_name,
        owner.birth_date,
        owner.address,
        owner.phone,
        owner.email,
        owner.is_active,
    )
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(sql, valores)
            owner_id = cursor.lastrowid
            creado = _buscar_por_id(cursor, owner_id)
            registrar_auditoria(
                cursor, "owners", "INSERT", owner_id, None, creado, usuario_desde(request)
            )
            cnx.commit()
            return creado


@router.get("", response_model=list[OwnerResponse])
def listar_owners():
    """Devuelve la lista completa de duenos registrados."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT {_COLUMNAS} FROM owners ORDER BY owner_id")
            return cursor.fetchall()


@router.get("/{owner_id}", response_model=OwnerResponse)
def obtener_owner(owner_id: int):
    """Devuelve un dueno por su ID. Responde 404 si no existe."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            return _exigir_existencia(cursor, owner_id)


@router.get("/{owner_id}/pets")
def listar_mascotas_de_owner(owner_id: int):
    """Devuelve todas las mascotas pertenecientes a un dueno, incluyendo el nombre de la especie."""
    sql = (
        "SELECT p.pet_id, p.name, s.name AS species_name, p.breed, p.gender, "
        "p.estimated_birth_date, p.weight_kg, p.is_alive "
        "FROM pets p "
        "INNER JOIN species s ON p.species_id = s.species_id "
        "WHERE p.owner_id = %s "
        "ORDER BY p.pet_id"
    )
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            _exigir_existencia(cursor, owner_id)
            cursor.execute(sql, (owner_id,))
            return cursor.fetchall()


@router.put("/{owner_id}", response_model=OwnerResponse)
def actualizar_owner(owner_id: int, datos: OwnerUpdate, request: Request):
    """Reemplaza todos los datos de un dueno existente (PUT)."""
    sql = (
        "UPDATE owners SET doc_type_id = %s, doc_number = %s, first_name = %s, "
        "last_name = %s, birth_date = %s, address = %s, phone = %s, email = %s, is_active = %s "
        "WHERE owner_id = %s"
    )
    valores = (
        datos.doc_type_id,
        datos.doc_number,
        datos.first_name,
        datos.last_name,
        datos.birth_date,
        datos.address,
        datos.phone,
        datos.email,
        datos.is_active,
        owner_id,
    )
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            anterior = _exigir_existencia(cursor, owner_id)
            cursor.execute(sql, valores)
            nuevo = _buscar_por_id(cursor, owner_id)
            registrar_auditoria(
                cursor, "owners", "UPDATE", owner_id, anterior, nuevo, usuario_desde(request)
            )
            cnx.commit()
            return nuevo


@router.patch("/{owner_id}", response_model=OwnerResponse)
def actualizar_owner_parcial(owner_id: int, datos: OwnerPatch, request: Request):
    """Actualiza unicamente los campos enviados de un dueno (PATCH)."""
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar.",
        )

    asignaciones = ", ".join(f"{columna} = %s" for columna in cambios)
    valores = list(cambios.values())

    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            anterior = _exigir_existencia(cursor, owner_id)
            cursor.execute(
                f"UPDATE owners SET {asignaciones} WHERE owner_id = %s",
                (*valores, owner_id),
            )
            nuevo = _buscar_por_id(cursor, owner_id)
            registrar_auditoria(
                cursor, "owners", "UPDATE", owner_id, anterior, nuevo, usuario_desde(request)
            )
            cnx.commit()
            return nuevo


@router.delete("/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_owner(owner_id: int, request: Request):
    """Elimina un dueno por su ID. Responde 409 si tiene mascotas asociadas."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            anterior = _exigir_existencia(cursor, owner_id)
            cursor.execute("DELETE FROM owners WHERE owner_id = %s", (owner_id,))
            registrar_auditoria(
                cursor, "owners", "DELETE", owner_id, anterior, None, usuario_desde(request)
            )
            cnx.commit()