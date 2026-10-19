"""
Configuración central del proyecto.

Las credenciales se leen desde el archivo .env
(NUNCA subir credenciales a GitHub).

Copien .env.example a .env y completen sus claves.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

RAIZ = Path(__file__).resolve().parents[1]

RUTA_DATOS = RAIZ / "data"
RUTA_DB = RUTA_DATOS / "coyuntura.db"
RUTA_SQL = RAIZ / "sql"


# ============================================================
# CREDENCIALES
# ============================================================

# Cargar variables desde el archivo .env ubicado en la raíz
# Cargar credenciales desde .env
load_dotenv(RAIZ / ".env", override=True)


# ------------------------------------------------------------
# Banco Central de Chile
# ------------------------------------------------------------

BCCH_USUARIO = os.getenv("BCCH_USUARIO", "")
BCCH_PASSWORD = os.getenv("BCCH_PASSWORD", "")
BCCH_TOKEN = os.getenv("BCCH_TOKEN", "")


# ------------------------------------------------------------
# FRED
# ------------------------------------------------------------

FRED_API_KEY = os.getenv("FRED_API_KEY", "")


# ============================================================
# CATÁLOGO DE SERIES DEL PROYECTO
#
# Formato:
# (codigo, nombre, frecuencia, unidad, id_tema)
#
# id_tema:
# 1 = Actividad
# 2 = Precios
# 3 = Mercado laboral
# 4 = Política monetaria
# 5 = Sector externo
# 6 = Internacional
# ============================================================


SERIES_BCCH = [

    # 1. IMACEC Total
    (
        "F032.IMC.IND.Z.Z.EP18.Z.Z.0.M",
        "IMACEC Total",
        "M",
        "indice 2018=100",
        1,
    ),

    # 2. EPU Chile
    (
        "F019.EPU.IND.91.M",
        "EPU Chile",
        "M",
        "indice",
        6,
    ),

    # 3. IMACEC Minero
    (
        "F032.IMC.IND.Z.Z.EP18.03.Z.0.M",
        "IMACEC Minero",
        "M",
        "indice 2018=100",
        1,
    ),

    # 4. IMACEC No Minero
    (
        "F032.IMC.IND.Z.Z.EP18.N03.Z.0.M",
        "IMACEC No Minero",
        "M",
        "indice 2018=100",
        1,
    ),

    # 5. Tasa de Política Monetaria
    (
        "F022.TPM.TIN.D001.NO.Z.D",
        "Tasa de Politica Monetaria",
        "D",
        "porcentaje",
        4,
    ),

    # 6. IPC
    (
        "F074.IPC.VAR.Z.Z.C.M",
        "IPC general historico, variacion mensual",
        "M",
        "variacion %",
        2,
    ),

    # 7. Tasa de desocupación
    (
        "F049.DES.TAS.INE.10.M",
        "Tasa de desocupacion total ajustada estacionalmente",
        "M",
        "porcentaje",
        3,
    ),

    # 8. Precio del cobre
    (
        "F019.PPB.PRE.40.M",
        "Precio cobre refinado BML",
        "M",
        "USD/libra",
        6,
    ),

    # 9. Precio del petróleo Brent
    (
        "F019.PPB.PRE.41AB.M",
        "Precio petroleo Brent",
        "M",
        "USD/barril",
        6,
    ),

    # 10. Tipo de cambio nominal
    (
        "F073.TCO.PRE.Z.D",
        "Tipo de cambio nominal dolar observado",
        "D",
        "CLP/USD",
        5,
    ),

    # 11. Actividad del comercio al por menor
    (
        "F034.VCC.IND.INE.2018.0.M",
        "Indice de actividad del comercio al por menor",
        "M",
        "indice 2018=100",
        1,
    ),

    # 12. IMCE Total
    (
        "G089.IME.IND.A0.M",
        "IMCE Total",
        "M",
        "indice",
        1,
    ),
]


# ============================================================
# SERIES FRED
# ============================================================

# Actualmente no utilizamos series de FRED.
SERIES_FRED = []