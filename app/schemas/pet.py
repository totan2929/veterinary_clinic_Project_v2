"""
Programa: app/schemas/pet.py
Objetivo: Definir los DTOs (schemas de Pydantic) para validar entradas y salidas
del recurso `pets` (mascotas/pacientes).
Fecha: 2026-11-24
Programador: <jorge andres garcia mojica>

Responsabilidad UNICA:
- Validar tipos, rangos y campos opcionales antes de ejecutar SQL en MySQL.
- Espejar las reglas de la tabla `pets` (genero M/F, peso positivo DECIMAL(5,2),
    chip unico opcional y llaves foraneas owner_id / species_id).
"""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Tipos reutilizables alineados con las columnas y CHECK de la tabla `pets`
# ---------------------------------------------------------------------------
OwnerId = Annotated[int, Field(ge=1, description="ID del dueno propietario (tabla owners)")]
SpeciesId = Annotated[int, Field(ge=1, le=255, description="ID de la especie (tabla species)")]
PetName = Annotated[str, Field(min_length=1, max_length=60)]
Breed = Annotated[str, Field(min_length=1, max_length=60)]
Gender = Literal["M", "F"]
WeightKg = Annotated[Decimal, Field(gt=0, le=Decimal("999.99"), max_digits=5, decimal_places=2)]
Color = Annotated[str, Field(min_length=1, max_length=50)]
Coat = Annotated[str, Field(min_length=1, max_length=50)]
ChipNumber = Annotated[str, Field(min_length=1, max_length=30)]
PhotoUrl = Annotated[str, Field(min_length=1, max_length=255)]


class PetBase(BaseModel):
    """Campos comunes para la creacion (POST) y actualizacion completa (PUT) de una mascota."""

    model_config = ConfigDict(str_strip_whitespace=True)

    owner_id: OwnerId
    name: PetName
    species_id: SpeciesId
    breed: Breed
    gender: Gender
    estimated_birth_date: date
    weight_kg: WeightKg
    color: Color | None = None
    coat: Coat | None = None
    has_chip: bool = False
    chip_number: ChipNumber | None = None
    is_neutered: bool = False
    is_alive: bool = True
    photo_url: PhotoUrl | None = None


class PetCreate(PetBase):
    """Schema de entrada requerido para registrar una mascota nueva (POST /pets)."""


class PetUpdate(PetBase):
    """Schema de entrada requerido para reemplazo completo de una mascota (PUT /pets/{pet_id})."""


class PetPatch(BaseModel):
    """Schema de entrada para actualizacion parcial (PATCH /pets/{pet_id}).

    Todos los campos son opcionales; solo se modifican los enviados en el cuerpo JSON.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    owner_id: OwnerId | None = None
    name: PetName | None = None
    species_id: SpeciesId | None = None
    breed: Breed | None = None
    gender: Gender | None = None
    estimated_birth_date: date | None = None
    weight_kg: WeightKg | None = None
    color: Color | None = None
    coat: Coat | None = None
    has_chip: bool | None = None
    chip_number: ChipNumber | None = None
    is_neutered: bool | None = None
    is_alive: bool | None = None
    photo_url: PhotoUrl | None = None


class PetResponse(PetBase):
    """Schema de salida devuelto por la API para una mascota."""

    pet_id: int
