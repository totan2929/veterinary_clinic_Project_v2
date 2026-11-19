from app.db_connection import get_connection

#toma una conexion del pool
with get_connection() as conexion1:
    #Creamos un cursor para guardar la consulta
    with conexion1.cursor() as cursor:
        #Le damos la instruccion del SELECT a cursor
        cursor.execute("SELECT * FROM clientes")
        #Se ejecuta la consulta y se entrega a resultado
        resultado = cursor.fetchall()