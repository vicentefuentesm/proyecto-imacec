import sqlite3
import pandas as pd


# Ruta de la base de datos
ruta_db = "data/coyuntura.db"

# Ruta de la consulta SQL
ruta_sql = "sql/03_revision_base.sql"


# Conectarse a la base
conexion = sqlite3.connect(ruta_db)


# ------------------------------------------------------------
# 1. Revisión general de todas las series
# ------------------------------------------------------------

with open(ruta_sql, "r", encoding="utf-8") as archivo:
    consulta = archivo.read()

resultado = pd.read_sql(consulta, conexion)

print("\nREVISION GENERAL DE LA BASE\n")
print(resultado.to_string(index=False))


# ------------------------------------------------------------
# 2. Comprobar que TPM y desempleo no sean datos demo
# ------------------------------------------------------------

consulta_control = """
SELECT
    s.nombre,
    o.fecha,
    o.valor
FROM observaciones AS o
JOIN series AS s
    ON o.id_serie = s.id_serie
WHERE s.nombre IN (
    'Tasa de Politica Monetaria',
    'Tasa de desocupacion total ajustada estacionalmente'
)
AND o.fecha = (
    SELECT MAX(o2.fecha)
    FROM observaciones AS o2
    WHERE o2.id_serie = o.id_serie
)
ORDER BY s.nombre;
"""

control = pd.read_sql(consulta_control, conexion)

print("\nCONTROL TPM Y DESEMPLEO\n")
print(control.to_string(index=False))


# Cerrar conexión
conexion.close()