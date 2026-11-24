"""
Programa: app/routers/pets.py
Objetivo: Exponer los endpoints HTTP (CRUD + PATCH) del recurso `pets` (mascotas).
Fecha: 2026-11-23
Programador: <jorge andres garcia mojica>

Responsabilidad UNICA:
- Recibir peticiones HTTP sobre /pets (datos ya validados por Pydantic).
- Ejecutar sentencias SQL parametrizadas (%s) usando conexiones del pool.
- Registrar cada escritura (INSERT, UPDATE, DELETE) en `audit_logs` dentro de la misma transaccion.
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.auditoria import registrar_auditoria, usuario_desde
from app.db_connection import get_connection
from app.errors import RESPUESTAS_ERROR
from app.schemas.pet import PetCreate, PetPatch, PetResponse, PetUpdate

router = APIRouter(prefix="/pets", tags=["Pets"], responses=RESPUESTAS_ERROR)

_COLUMNAS = (
    "pet_id, owner_id, name, species_id, breed, gender, estimated_birth_date, "
    "weight_kg, color, coat, has_chip, chip_number, is_neutered, is_alive, photo_url"
)


def _buscar_por_id(cursor, pet_id: int) -> dict | None:
    """Consulta una mascota por su llave primaria `pet_id`.

    Args:
        cursor: Cursor MySQL activo (dictionary=True).
        pet_id (int): Identificador de la mascota.

    Returns:
        dict | None: Registro encontrado o None si no existe.
    """
    cursor.execute(f"SELECT {_COLUMNAS} FROM pets WHERE pet_id = %s", (pet_id,))
    return cursor.fetchone()


def _exigir_existencia(cursor, pet_id: int) -> dict:
    """Devuelve la mascota solicitada o lanza HTTP 404 si no existe."""
    pet = _buscar_por_id(cursor, pet_id)
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe una mascota con el ID {pet_id}.",
        )
    return pet


@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def crear_pet(pet: PetCreate, request: Request):
    """Registra una mascota nueva asociada a un dueno y especie existentes."""
    sql = (
        "INSERT INTO pets "
        "(owner_id, name, species_id, breed, gender, estimated_birth_date, weight_kg, "
        "color, coat, has_chip, chip_number, is_neutered, is_alive, photo_url) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    valores = (
        pet.owner_id,
        pet.name,
        pet.species_id,
        pet.breed,
        pet.gender,
        pet.estimated_birth_date,
        pet.weight_kg,
        pet.color,
        pet.coat,
        pet.has_chip,
        pet.chip_number,
        pet.is_neutered,
        pet.is_alive,
        pet.photo_url,
    )
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(sql, valores)
            pet_id = cursor.lastrowid
            creado = _buscar_por_id(cursor, pet_id)
            registrar_auditoria(
                cursor, "pets", "INSERT", pet_id, None, creado, usuario_desde(request)
            )
            cnx.commit()
            return creado


@router.get("", response_model=list[PetResponse])
def listar_pets():
    """Devuelve la lista completa de mascotas registradas."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT {_COLUMNAS} FROM pets ORDER BY pet_id")
            return cursor.fetchall()


@router.get("/{pet_id}", response_model=PetResponse)
def obtener_pet(pet_id: int):
    """Devuelve una mascota por su ID. Responde 404 si no existe."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            return _exigir_existencia(cursor, pet_id)


@router.put("/{pet_id}", response_model=PetResponse)
def actualizar_pet(pet_id: int, datos: PetUpdate, request: Request):
    """Reemplaza todos los datos de una mascota existente (PUT)."""
    sql = (
        "UPDATE pets SET owner_id = %s, name = %s, species_id = %s, breed = %s, "
        "gender = %s, estimated_birth_date = %s, weight_kg = %s, color = %s, coat = %s, "
        "has_chip = %s, chip_number = %s, is_neutered = %s, is_alive = %s, photo_url = %s "
        "WHERE pet_id = %s"
    )
    valores = (
        datos.owner_id,
        datos.name,
        datos.species_id,
        datos.breed,
        datos.gender,
        datos.estimated_birth_date,
        datos.weight_kg,
        datos.color,
        datos.coat,
        datos.has_chip,
        datos.chip_number,
        datos.is_neutered,
        datos.is_alive,
        datos.photo_url,
        pet_id,
    )
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            anterior = _exigir_existencia(cursor, pet_id)
            cursor.execute(sql, valores)
            nuevo = _buscar_por_id(cursor, pet_id)
            registrar_auditoria(
                cursor, "pets", "UPDATE", pet_id, anterior, nuevo, usuario_desde(request)
            )
            cnx.commit()
            return nuevo


@router.patch("/{pet_id}", response_model=PetResponse)
def actualizar_pet_parcial(pet_id: int, datos: PetPatch, request: Request):
    """Actualiza unicamente los campos enviados de una mascota (PATCH)."""
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
            anterior = _exigir_existencia(cursor, pet_id)
            cursor.execute(
                f"UPDATE pets SET {asignaciones} WHERE pet_id = %s",
                (*valores, pet_id),
            )
            nuevo = _buscar_por_id(cursor, pet_id)
            registrar_auditoria(
                cursor, "pets", "UPDATE", pet_id, anterior, nuevo, usuario_desde(request)
            )
            cnx.commit()
            return nuevo


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pet(pet_id: int, request: Request):
    """Elimina una mascota por su ID y registra el evento en `audit_logs`."""
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            anterior = _exigir_existencia(cursor, pet_id)
            cursor.execute("DELETE FROM pets WHERE pet_id = %s", (pet_id,))
            registrar_auditoria(
                cursor, "pets", "DELETE", pet_id, anterior, None, usuario_desde(request)
            )
            cnx.commit()
