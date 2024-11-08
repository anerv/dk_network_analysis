ALTER TABLE
    socio
ADD
    COLUMN IF NOT EXISTS urban_pct DECIMAL;

WITH inter AS (
    SELECT
        so.id AS id,
        SUM(
            ST_Area(ST_Intersection(so.geometry, ub.geometry))
        ) AS intersection_area
    FROM
        socio AS so,
        urban_areas AS ub
    WHERE
        ST_Intersects(so.geometry, ub.geometry)
    GROUP BY
        so.id
)
UPDATE
    socio
SET
    urban_pct = (
        inter.intersection_area / ST_Area(socio.geometry)
    ) * 100
FROM
    inter
WHERE
    socio.id = inter.id;

UPDATE
    socio
SET
    urban_pct = 0
WHERE
    urban_pct IS NULL;