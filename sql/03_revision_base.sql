
-- Etapa 3: Revisión de la base antes de analizar
-- ============================================================
-- Permite comprobar:
-- 1. Cantidad de observaciones por serie.
-- 2. Fecha inicial y final.
-- 3. Frecuencia y unidad de cada serie.
-- ============================================================

SELECT
    t.tema,
    s.nombre,
    s.frecuencia,
    s.unidad,
    COUNT(o.valor) AS n_obs,
    MIN(o.fecha) AS desde,
    MAX(o.fecha) AS hasta

FROM temas AS t

LEFT JOIN series AS s
    ON s.id_tema = t.id_tema

LEFT JOIN observaciones AS o
    ON o.id_serie = s.id_serie

GROUP BY
    t.tema,
    s.nombre,
    s.frecuencia,
    s.unidad

ORDER BY
    t.tema,
    n_obs;