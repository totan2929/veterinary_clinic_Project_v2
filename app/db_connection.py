"""
Programa: app/db_connection.py
Objetivo: Administrar el pool de conexiones reutilizables hacia MySQL.
Fecha: 2026-11-24
Programador: Jonathan Cañola Salazar - Jorge Andrés García Mojica

Responsabilidad UNICA:
  - Leer la configuracion desde el archivo .env.
  - Crear y administrar el pool de conexiones reutilizables (patron singleton).
  - Entregar conexiones limpias sin contener logica de negocio ni SQL.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from mysql.connector import pooling
from mysql.connector.pooling import PooledMySQLConnection

# Raiz del proyecto: carpeta que contiene a 'app/' y donde vive .env
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga el archivo .env usando ruta absoluta
load_dotenv(BASE_DIR / ".env")

POOL_NAME = "veterinary_clinic_pool"
POOL_SIZE = 16

# Unica instancia del pool en memoria (patron singleton / inicializacion perezosa)
_pool: pooling.MySQLConnectionPool | None = None


def _crear_pool() -> pooling.MySQLConnectionPool:
    """Construye el pool de conexiones leyendo las credenciales desde .env."""
    return pooling.MySQLConnectionPool(
        pool_name=POOL_NAME,
        pool_size=POOL_SIZE,
        # Reinicia el estado de la sesion al devolver una conexion al pool
        pool_reset_session=True,
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset=os.getenv("DB_CHARSET", "utf8mb4"),
    )


def get_pool() -> pooling.MySQLConnectionPool:
    """Devuelve el pool de conexiones, creandolo solo la primera vez que se solicita."""
    global _pool
    if _pool is None:
        _pool = _crear_pool()
    return _pool


def get_connection() -> PooledMySQLConnection:
    """Entrega una conexion disponible del pool (usar siempre con bloque `with`)."""
    return get_pool().get_connection()