CREATE INDEX IF NOT EXISTS hex_geom_ix ON hex_grid USING GIST(geometry);

CREATE INDEX IF NOT EXISTS urban_geom_ix ON urban_areas USING GIST (geometry);

ALTER TABLE
    hex_grid
ADD
    COLUMN IF NOT EXISTS urban_pct DECIMAL;

WITH inter AS (
    SELECT
        h.hex_id,
        SUM(
            ST_Area(ST_Intersection(h.geometry, ub.geometry))
        ) AS intersection_area
    FROM
        hex_grid AS h,
        urban_areas AS ub
    WHERE
        ST_Intersects(h.geometry, ub.geometry)
    GROUP BY
        h.hex_id
)
UPDATE
    hex_grid
SET
    urban_pct = (
        inter.intersection_area / ST_Area(hex_grid.geometry)
    ) * 100
FROM
    inter
WHERE
    hex_grid.hex_id = inter.hex_id;

UPDATE
    hex_grid
SET
    urban_pct = 0
WHERE
    urban_pct IS NULL;

ALTER TABLE
    hex_grid
ADD
    COLUMN IF NOT EXISTS population DECIMAL,
ADD
    COLUMN IF NOT EXISTS pop_density DECIMAL;

UPDATE
    hex_grid
SET
    population = h3_population.population
FROM
    h3_population
WHERE
    hex_grid.hex_id = h3_population.hex_id;

UPDATE
    hex_grid
SET
    pop_density = population / ST_Area(geometry) * 1000000;

DROP TABLE IF EXISTS h3_population;