-- ============================================================
-- Etapa 4: Consultas SQL
-- Proyecto IMACEC
-- ============================================================

-- ------------------------------------------------------------
-- Consulta 1: JOIN entre observaciones, series y temas
-- ------------------------------------------------------------
-- Objetivo:
-- Obtener cada observación junto con el nombre de la serie,
-- su tema, frecuencia y unidad.
--
-- Esta consulta permite trabajar con los datos económicos
-- de forma legible, en vez de usar solamente el id_serie.
-- ------------------------------------------------------------

SELECT
    o.fecha,
    s.nombre,
    t.tema,
    s.frecuencia,
    s.unidad,
    o.valor

FROM observaciones AS o

JOIN series AS s
    ON o.id_serie = s.id_serie

JOIN temas AS t
    ON s.id_tema = t.id_tema

ORDER BY
    s.nombre,
    o.fecha;

    -- ------------------------------------------------------------
-- Consulta 2: GROUP BY para llevar series diarias a frecuencia mensual
-- ------------------------------------------------------------
-- Objetivo:
-- Calcular un promedio mensual para las series que originalmente
-- tienen frecuencia diaria.
--
-- Esto permite trabajar todas las series posteriormente
-- en una frecuencia comparable.
-- ------------------------------------------------------------

SELECT
    s.nombre,
    s.unidad,
    strftime('%Y-%m', o.fecha) AS mes,
    ROUND(AVG(o.valor), 2) AS promedio_mensual,
    COUNT(o.valor) AS n_datos

FROM observaciones AS o

JOIN series AS s
    ON o.id_serie = s.id_serie

WHERE s.frecuencia = 'D'

GROUP BY
    s.nombre,
    s.unidad,
    strftime('%Y-%m', o.fecha)

ORDER BY
    s.nombre,
    mes;

    -- ------------------------------------------------------------
-- Consulta 3: Función de ventana
-- Variación interanual del IMACEC y sus componentes
-- ------------------------------------------------------------
-- Objetivo:
-- Calcular la variación porcentual respecto del mismo mes
-- del año anterior para el IMACEC Total, Minero y No Minero.
--
-- LAG(valor, 12) recupera el valor de 12 meses atrás.
-- PARTITION BY evita mezclar observaciones de series distintas.
-- ORDER BY mes mantiene el orden temporal.
-- ------------------------------------------------------------

WITH imacec_mensual AS (

    SELECT
        o.id_serie,
        s.nombre,
        strftime('%Y-%m', o.fecha) AS mes,
        AVG(o.valor) AS valor

    FROM observaciones AS o

    JOIN series AS s
        ON o.id_serie = s.id_serie

    WHERE s.nombre IN (
        'IMACEC Total',
        'IMACEC Minero',
        'IMACEC No Minero'
    )

    GROUP BY
        o.id_serie,
        s.nombre,
        strftime('%Y-%m', o.fecha)
)

SELECT
    nombre,
    mes,
    ROUND(valor, 2) AS valor,

    ROUND(
        LAG(valor, 12) OVER (
            PARTITION BY id_serie
            ORDER BY mes
        ),
        2
    ) AS valor_hace_12_meses,

    ROUND(
        100.0 * (
            valor /
            LAG(valor, 12) OVER (
                PARTITION BY id_serie
                ORDER BY mes
            ) - 1
        ),
        2
    ) AS variacion_interanual_pct

FROM imacec_mensual

ORDER BY
    nombre,
    mes;