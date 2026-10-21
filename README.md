Monitor de Coyuntura y Proyección Macroeconómica — IMACEC

Proyecto semestral de Ciencia de Datos para Economía (ICO09425).

1. Descripción

El proyecto tiene como variable objetivo el IMACEC (Índice Mensual de Actividad Económica).

La pregunta que guía el trabajo es:

¿Cuál es nuestra proyección para la variación interanual del IMACEC durante los próximos 12 meses, en qué evidencia y modelos se sustenta, y cuáles son los principales riesgos del escenario?

Para analizar la actividad económica se utilizan 12 series obtenidas desde la API del Banco Central de Chile, incluyendo:

IMACEC Total.

IMACEC Minero.

IMACEC No Minero.

Índice de Incertidumbre de Política Económica (EPU).

Tasa de Política Monetaria (TPM).

IPC.

Tasa de desocupación.

Precio del cobre.

Precio del petróleo Brent.

Tipo de cambio nominal.

Índice de actividad del comercio al por menor.

Índice de Confianza Empresarial (IMCE).

Los datos se almacenan en una base de datos relacional SQLite compuesta principalmente por las tablas temas, series y observaciones.

2. Requisitos

Se requiere tener instalado:

Python.

pip.

Git.

Las dependencias del proyecto se encuentran en requirements.txt.

Para instalarlas:

pip install -r requirements.txt

3. Credenciales

Las credenciales utilizadas para acceder a las APIs se almacenan localmente en un archivo .env.

Primero se debe copiar el archivo de ejemplo:

Windows PowerShell

Copy-Item .env.example .env

Luego se deben completar las credenciales correspondientes dentro de .env.

El archivo .env no se sub a GitHub y está excluido mediante .gitignore.

4. Reproducción del proyecto

Clonar el repositorio:

git clone https://github.com/vicentefuentesm/proyecto-imacec.git
cd proyecto-imacec

Instalar las dependencias:

pip install -r requirements.txt

Crear y configurar el archivo .env según la sección anterior.

4.1. Descargar y cargar los datos

La fecha de corte utilizada para el Hito 2 es el 31 de agosto de 2026.

Ejecutar:

python src/carga_db.py --hasta 2026-08-31

La carga correcta debe terminar con:

12 series cargadas.

Un [OK] por cada serie.

Ningún [ERROR].

10.299 observaciones cargadas o actualizadas.

La base se genera localmente en:

data/coyuntura.db

La carpeta data/ no se sube al repositorio.

4.2. Verificar la base de datos

Ejecutar:

python src/verificar_base.py

Este script revisa para cada serie:

cantidad de observaciones;

fecha inicial;

fecha final;

frecuencia;

unidad.

También se revisan los valores recientes de la TPM y la tasa de desocupación para comprobar que la base contiene datos reales y no datos generados con el modo demo.

4.3. Ejecutar las consultas SQL

Ejecutar:

python src/consultas.py

Las consultas utilizadas se encuentran en:

sql/02_consultas_imacec.sql

El archivo contiene tres consultas principales:

JOIN: relaciona observaciones, series y temas.

GROUP BY: lleva las series de frecuencia diaria a frecuencia mensual mediante promedios mensuales.

Función de ventana: calcula la variación interanual del IMACEC utilizando LAG, PARTITION BY y ORDER BY.

La función de ventana se calcula de manera independiente para cada serie, evitando mezclar observaciones correspondientes a indicadores distintos.

5. Estructura del repositorio

proyecto-imacec/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── coyuntura.db            # Se genera localmente y no se sube
│
├── docs/
│   └── Hito2_Imacec.xlsx
│
├── sql/
│   ├── 01_esquema.sql
│   ├── 02_consultas_imacec.sql
│   └── 03_revision_base.sql
│
├── src/
│   ├── config.py
│   ├── extraccion.py
│   ├── carga_db.py
│   ├── verificar_base.py
│   ├── consultas.py
│   └── exportar_powerbi.py
│
└── dashboard/
    └── README_powerbi.md

6. Base de datos

La base utiliza SQLite y contiene tres tablas principales:

temas

Clasifica las series según su área económica, por ejemplo actividad, precios, mercado laboral, política monetaria y sector externo.

series

Contiene el catálogo de indicadores económicos, incluyendo nombre, fuente, frecuencia, unidad y tema.

observaciones

Contiene los valores observados de cada serie económica en cada fecha.

Las tablas están relacionadas mediante identificadores y llaves foráneas.

7. Consultas SQL

Las consultas del Hito 2 fueron diseñadas para cumplir los requerimientos de análisis sobre la base relacional.

Se utilizan:

JOIN para relacionar las tablas de la base.

GROUP BY para agregar las observaciones diarias a frecuencia mensual.

AVG() para calcular promedios mensuales.

LAG() para recuperar el valor de una serie doce meses atrás.

PARTITION BY para realizar el cálculo independientemente dentro de cada serie.

ORDER BY para mantener el orden temporal de las observaciones.

Por ejemplo, la variación interanual del IMACEC se calcula comparando cada valor mensual con el correspondiente a doce meses atrás.

8. Consideraciones de reproducibilidad

Para reproducir correctamente el proyecto:

No utilizar el modo --demo para la entrega.

Mantener las credenciales exclusivamente en .env.

No subir data/coyuntura.db a GitHub.

Utilizar la fecha de corte 2026-08-31.

Instalar previamente las dependencias desde requirements.txt.

Ejecutar los scripts desde la raíz del repositorio.