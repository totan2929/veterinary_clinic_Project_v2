"""
    Responsabilidad UNICA: entregar conexiones a la base de datos 

    Que hace:
        Leer la configuracion desde .env
        Crear y administrar el POOL de conexiones reutilizables

    Que no hace:
        Contener logica del negocio
        No valida ni sanitiza entradas de usuario
        No ejecuta SQL del negocio
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from mysql.connector import pooling
from mysql.connector.pooling import PooledMySQLConnection

PooledMySQLConnection

#Raiz del proyecto: la carpeta que contiene app/ y donde vive .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent

#Cargar el archivo .env usando la ruta absoluta para que funcione sin
#importar desde donde se ejecute el proyecto
load_dotenv(BASE_DIR / ".env")

# Crear el nombre del pool y cuantas conexiones mantiene abiertas 
# de forma reutilizable
POOL_NAME = "clientesapp_pool"
POOL_SIZE = 5

#Variable de modulo que guarda la unica instalacia del pool (patron singleton)
_pool: pooling.MySQLConnectionPool | None = None

def _crear_pool() -> pooling.MySQLConnectionPool:
    #Contruye el pool leyendo las credenciales desde las variables
    # de entorno.
    return pooling.MySQLConnectionPool(
        pool_name=POOL_NAME,
        pool_size=POOL_SIZE,
        #Reinicia el estado de la sesion al devolver una conexion al pool
        pool_reset_session=True,
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset=os.getenv("DB_CHARSET"),
    )

def get_pool() -> pooling.MySQLConnectionPool:
    """Devuelve el pool, creandolo la primera vez que se solicita"""
    global _pool
    if _pool is None:
        _pool = _crear_pool()
    return _pool

def get_connection() -> PooledMySQLConnection:
    """
        Entrega una conexion del pool.
        Uso recomendado: (la conexion siempre devuelve al pool)
    """
    return get_pool().get_connection()