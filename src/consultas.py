import sqlite3
import pandas as pd


# Ruta de la base de datos
ruta_db = "data/coyuntura.db"

# Ruta del archivo SQL
ruta_sql = "sql/02_consultas_imacec.sql"


# Leer archivo SQL
with open(ruta_sql, "r", encoding="utf-8") as archivo:
    contenido = archivo.read()


# Separar las consultas por ;
consultas = [
    consulta.strip()
    for consulta in contenido.split(";")
    if consulta.strip()
]


# Conectarse a la base
conexion = sqlite3.connect(ruta_db)


# Ejecutar cada consulta
for numero, consulta in enumerate(consultas, start=1):

    resultado = pd.read_sql(consulta, conexion)

    print(f"\nCONSULTA {numero}\n")
    print(resultado.head(20).to_string(index=False))


# Cerrar conexión
conexion.close()