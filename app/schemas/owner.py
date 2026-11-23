"""
Programa: app/schemas/owner.py
Objetivo: Definir los DTOs (schemas de Pydantic) para validar entradas y salidas
          del recurso `owners` (duenos de mascotas).
Fecha: 2026-11-22
Programador: <Tu Nombre>

Responsabilidad UNICA:
  - Validar tipos, longitudes y patrones antes de ejecutar SQL en MySQL.
  - Espejar las reglas y CHECK de la tabla `owners` (doc_number 8-10 digitos,
    phone 10 digitos, email valido).
"""

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------------------------------------------------------------------------
# Tipos reutilizables alineados con las columnas y CHECK de la tabla `owners`
# ---------------------------------------------------------------------------
DocTypeId = Annotated[int, Field(ge=1, le=255, description="ID del tipo de documento (tabla document_types)")]
DocNumber = Annotated[str, Field(pattern=r"^[0-9]{8,10}$", description="Numero de documento (8 a 10 digitos)")]
FirstName = Annotated[str, Field(min_length=1, max_length=80)]
LastName = Annotated[str, Field(min_length=1, max_length=80)]
Address = Annotated[str, Field(min_length=1, max_length=100)]
Phone = Annotated[str, Field(pattern=r"^[0-9]{10}$", description="Telefono celular de 10 digitos")]
Email = Annotated[EmailStr, Field(max_length=70)]


class OwnerBase(BaseModel):
    """Campos comunes para la creacion (POST) y actualizacion completa (PUT) de un dueno."""

    # Elimina espacios en blanco sobrantes al inicio y al final de cada cadena
    model_config = ConfigDict(str_strip_whitespace=True)

    doc_type_id: DocTypeId
    doc_number: DocNumber
    first_name: FirstName
    last_name: LastName
    birth_date: date
    address: Address
    phone: Phone
    email: Email
    is_active: bool = True


class OwnerCreate(OwnerBase):
    """Schema de entrada requerido para registrar un dueno nuevo (POST /owners)."""


class OwnerUpdate(OwnerBase):
    """Schema de entrada requerido para reemplazo completo de un dueno (PUT /owners/{owner_id})."""


class OwnerPatch(BaseModel):
    """Schema de entrada para actualizacion parcial (PATCH /owners/{owner_id}).

    Todos los campos son opcionales; solo se actualizan los que se envien en el JSON.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    doc_type_id: DocTypeId | None = None
    doc_number: DocNumber | None = None
    first_name: FirstName | None = None
    last_name: LastName | None = None
    birth_date: date | None = None
    address: Address | None = None
    phone: Phone | None = None
    email: Email | None = None
    is_active: bool | None = None


class OwnerResponse(OwnerBase):
    """Schema de salida devuelto por la API, incluyendo llave primaria y fecha de creacion."""

    owner_id: int
    created_at: datetime | None = None