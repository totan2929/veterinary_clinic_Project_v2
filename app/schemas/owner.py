"""
Programa: app/schemas/owner.py
Objetivo: Definir los modelos Pydantic de entrada, actualizacion y salida para owners.
Fecha: 2026-11-24
Programador: <jorge andres garcia moica>

Responsabilidad UNICA:
- Validar tipos, longitudes y formatos de los datos de duenos antes de tocar MySQL.
- Serializar las respuestas JSON de owners alineadas con el esquema de la BD.
"""

from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator


class OwnerBase(BaseModel):
    """Campos compartidos para creacion y actualizacion completa de un dueno."""

    doc_type_id: int = Field(..., ge=1, le=255, description="ID del tipo de documento (catalogo)")
    doc_number: int = Field(
        ...,
        ge=100000,
        le=2147483647,
        description="Numero de documento entero (unico)",
    )
    first_name: str = Field(..., min_length=2, max_length=80, description="Nombres del dueno")
    last_name: str = Field(..., min_length=2, max_length=80, description="Apellidos del dueno")
    birth_date: date = Field(..., description="Fecha de nacimiento (YYYY-MM-DD)")
    address: str = Field(..., min_length=4, max_length=100, description="Direccion de residencia")
    phone: str = Field(..., min_length=7, max_length=10, description="Telefono de contacto (solo digitos)")
    email: EmailStr = Field(..., max_length=70, description="Correo electronico (unico)")

    @field_validator("first_name", "last_name", "address")
    @classmethod
    def limpiar_espacios(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio:
            raise ValueError("El campo no puede estar vacio.")
        return limpio

    @field_validator("phone")
    @classmethod
    def validar_telefono(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio.isdigit():
            raise ValueError("El telefono debe contener unicamente digitos.")
        return limpio


class OwnerCreate(OwnerBase):
    """Esquema para POST /owners."""


class OwnerUpdate(OwnerBase):
    """Esquema para PUT /owners/{owner_id} (reemplazo completo)."""


class OwnerPatch(BaseModel):
    """Esquema para PATCH /owners/{owner_id} (actualizacion parcial)."""

    doc_type_id: int | None = Field(default=None, ge=1, le=255)
    doc_number: int | None = Field(default=None, ge=100000, le=2147483647)
    first_name: str | None = Field(default=None, min_length=2, max_length=80)
    last_name: str | None = Field(default=None, min_length=2, max_length=80)
    birth_date: date | None = Field(default=None)
    address: str | None = Field(default=None, min_length=4, max_length=100)
    phone: str | None = Field(default=None, min_length=7, max_length=10)
    email: EmailStr | None = Field(default=None, max_length=70)

    @field_validator("first_name", "last_name", "address")
    @classmethod
    def limpiar_espacios_opcional(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = valor.strip()
        if not limpio:
            raise ValueError("El campo no puede estar vacio.")
        return limpio

    @field_validator("phone")
    @classmethod
    def validar_telefono_opcional(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = valor.strip()
        if not limpio.isdigit():
            raise ValueError("El telefono debe contener unicamente digitos.")
        return limpio


class OwnerResponse(OwnerBase):
    """Esquema de respuesta devuelto por los endpoints de owners."""

    owner_id: int