"""
Extracción de series económicas desde APIs oficiales.

Fuentes soportadas:
  - Banco Central de Chile (Base de Datos Estadísticos, API SieteRestWS)
  - FRED (Federal Reserve Bank of St. Louis)

Incluye además un MODO DEMO que genera series sintéticas con la misma
estructura, para que puedan probar el pipeline completo (base de datos,
SQL, análisis, Power BI) ANTES de tener sus credenciales.

Uso desde la raíz del repositorio:
    python src/extraccion.py
    python src/extraccion.py --demo
    python src/extraccion.py --hasta 2026-07-31
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

import numpy as np
import pandas as pd
import requests

try:
    import config
except ImportError:
    from src import config  # type: ignore


URL_BCCH = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
URL_FRED = "https://api.stlouisfed.org/fred/series/observations"


# ------------------------------------------------------------
# Seguridad: nunca dejar una credencial en un mensaje de error
# ------------------------------------------------------------
def enmascarar(texto: str) -> str:
    """Reemplaza por '***' cualquier credencial que aparezca en el texto."""

    secretos = [
        getattr(config, "FRED_API_KEY", ""),
        getattr(config, "BCCH_TOKEN", ""),
        getattr(config, "BCCH_PASSWORD", ""),
        getattr(config, "BCCH_USUARIO", ""),
    ]

    for secreto in secretos:
        if secreto:
            texto = texto.replace(secreto, "***")

    return texto


def pedir_json(url: str, params: dict) -> dict:
    """Hace una petición HTTP y devuelve la respuesta JSON."""

    try:
        respuesta = requests.get(
            url,
            params=params,
            timeout=60,
        )

        respuesta.raise_for_status()

        return respuesta.json()

    except requests.RequestException as e:
        raise RuntimeError(
            enmascarar(str(e))
        ) from None

    except ValueError:
        raise RuntimeError(
            "La API respondió, pero la respuesta no era un JSON válido."
        ) from None


# ------------------------------------------------------------
# Banco Central de Chile
# ------------------------------------------------------------
def extraer_serie_bcch(
    codigo: str,
    desde: str = "2010-01-01",
    hasta: str | None = None,
) -> pd.DataFrame:
    """
    Descarga una serie desde la API REST del Banco Central de Chile
    y devuelve un DataFrame con las columnas fecha y valor.
    """

    if not getattr(config, "BCCH_TOKEN", ""):
        raise RuntimeError(
            "Falta BCCH_TOKEN en el archivo .env."
        )

    hasta = hasta or date.today().isoformat()

    params = {
        "token": config.BCCH_TOKEN,
        "function": "GetSeries",
        "timeseries": codigo,
        "firstdate": desde,
        "lastdate": hasta,
    }

    contenido = pedir_json(
        URL_BCCH,
        params,
    )

    codigo_respuesta = contenido.get("Codigo")
    descripcion = contenido.get("Descripcion", "")

    if codigo_respuesta not in (0, "0", None):
        raise RuntimeError(
            f"Error BCCh {codigo_respuesta}: {descripcion}"
        )

    series = contenido.get("Series") or {}
    observaciones = series.get("Obs") or []

    if not observaciones:
        raise ValueError(
            f"La API del BCCh no devolvió observaciones para '{codigo}'. "
            f"Respuesta: {descripcion or 'sin descripción'}"
        )

    df = pd.DataFrame(observaciones)

    if "indexDateString" not in df.columns:
        raise ValueError(
            f"La respuesta del BCCh para '{codigo}' no contiene "
            "'indexDateString'."
        )

    if "value" not in df.columns:
        raise ValueError(
            f"La respuesta del BCCh para '{codigo}' no contiene 'value'."
        )

    df["fecha"] = pd.to_datetime(
        df["indexDateString"],
        format="%d-%m-%Y",
        errors="coerce",
    )

    df["valor"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    df = (
        df[["fecha", "valor"]]
        .dropna()
        .sort_values("fecha")
        .reset_index(drop=True)
    )

    if df.empty:
        raise ValueError(
            f"La serie '{codigo}' fue descargada, pero no quedaron "
            "observaciones válidas después de procesarla."
        )

    return df


# ------------------------------------------------------------
# FRED
# ------------------------------------------------------------
def extraer_serie_fred(
    codigo: str,
    desde: str = "2010-01-01",
    hasta: str | None = None,
) -> pd.DataFrame:
    """
    Descarga una serie desde FRED y devuelve un DataFrame
    con las columnas fecha y valor.
    """

    if not getattr(config, "FRED_API_KEY", ""):
        raise RuntimeError(
            "Falta FRED_API_KEY en el archivo .env."
        )

    params = {
        "series_id": codigo,
        "api_key": config.FRED_API_KEY,
        "file_type": "json",
        "observation_start": desde,
        "observation_end": hasta or date.today().isoformat(),
    }

    contenido = pedir_json(
        URL_FRED,
        params,
    )

    observaciones = contenido.get("observations", [])

    if not observaciones:
        raise ValueError(
            f"La API de FRED no devolvió observaciones para '{codigo}'."
        )

    df = pd.DataFrame(observaciones)

    df["fecha"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["valor"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    return (
        df[["fecha", "valor"]]
        .dropna()
        .sort_values("fecha")
        .reset_index(drop=True)
    )


# ------------------------------------------------------------
# Modo demo
# ------------------------------------------------------------
def generar_serie_demo(
    codigo: str,
    frecuencia: str,
    semilla: int,
    hasta: str | None = None,
) -> pd.DataFrame:
    """
    Genera una serie sintética SIN significado económico.

    Estos datos solo sirven para probar el pipeline.
    No deben utilizarse para análisis ni proyecciones.
    """

    fin = hasta or date.today().isoformat()

    rng = np.random.default_rng(semilla)

    if frecuencia == "D":
        fechas = pd.date_range(
            "2014-01-01",
            fin,
            freq="B",
        )
    else:
        fechas = pd.date_range(
            "2010-01-01",
            fin,
            freq="MS",
        )

    n = len(fechas)
    t = np.arange(n)

    tendencia = 100 + 0.05 * t

    estacionalidad = 3 * np.sin(
        2 * np.pi * t / (252 if frecuencia == "D" else 12)
    )

    ruido = (
        rng.normal(0, 1.5, n)
        .cumsum()
        * 0.3
    )

    valores = (
        tendencia
        + estacionalidad
        + ruido
    )

    return pd.DataFrame(
        {
            "fecha": fechas,
            "valor": np.round(valores, 3),
        }
    )


# ------------------------------------------------------------
# Orquestación
# ------------------------------------------------------------
def extraer_todo(
    demo: bool = False,
    desde: str = "2010-01-01",
    hasta: str | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Extrae todas las series definidas en config.py.

    Devuelve:
        dict[str, DataFrame]

    Si una serie falla, se informa el error y el proceso continúa.
    """

    resultados: dict[str, pd.DataFrame] = {}

    catalogo = (
        config.SERIES_BCCH
        + config.SERIES_FRED
    )

    fallidas: list[str] = []

    for i, (
        codigo,
        nombre,
        frecuencia,
        _unidad,
        _tema,
    ) in enumerate(catalogo):

        try:

            if demo:

                df = generar_serie_demo(
                    codigo,
                    frecuencia,
                    semilla=i,
                    hasta=hasta,
                )

            elif (
                codigo,
                nombre,
                frecuencia,
                _unidad,
                _tema,
            ) in config.SERIES_BCCH:

                df = extraer_serie_bcch(
                    codigo,
                    desde=desde,
                    hasta=hasta,
                )

            else:

                df = extraer_serie_fred(
                    codigo,
                    desde=desde,
                    hasta=hasta,
                )

            resultados[codigo] = df

            ultima = (
                df["fecha"].max().date()
                if len(df)
                else "sin datos"
            )

            print(
                f"  [OK] {nombre}: "
                f"{len(df)} observaciones, "
                f"hasta {ultima}"
            )

        except Exception as e:

            fallidas.append(nombre)

            print(
                f"  [ERROR] {nombre} ({codigo}): "
                f"{enmascarar(str(e))}"
            )

    if fallidas:

        print(
            f"\n  ATENCION: "
            f"{len(fallidas)} de {len(catalogo)} "
            f"series fallaron: "
            f"{', '.join(fallidas)}"
        )

    return resultados


# ------------------------------------------------------------
# Ejecución directa
# ------------------------------------------------------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Extracción de series económicas"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Generar datos sintéticos de prueba",
    )

    parser.add_argument(
        "--desde",
        default="2010-01-01",
        metavar="AAAA-MM-DD",
        help="Primera fecha a solicitar",
    )

    parser.add_argument(
        "--hasta",
        default=None,
        metavar="AAAA-MM-DD",
        help="Fecha de corte",
    )

    args = parser.parse_args()

    modo = (
        "DEMO (datos sintéticos)"
        if args.demo
        else "APIs oficiales"
    )

    corte = (
        args.hasta
        or f"{date.today().isoformat()} (hoy)"
    )

    print(
        f"Extrayendo series | "
        f"modo: {modo} | "
        f"desde {args.desde} "
        f"hasta {corte}"
    )

    series = extraer_todo(
        demo=args.demo,
        desde=args.desde,
        hasta=args.hasta,
    )

    if not series:
        sys.exit(
            "No se extrajo ninguna serie. "
            "Revisen credenciales y códigos."
        )

    print(
        f"Total: {len(series)} series extraídas."
    )