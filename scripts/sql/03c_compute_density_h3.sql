DROP TABLE IF EXISTS density.density_h3;

DROP TABLE IF EXISTS density.split_edges_h3;

DROP TABLE IF EXISTS h3_edges;

DROP TABLE IF EXISTS density.h3_buffer;

CREATE INDEX IF NOT EXISTS lts_access_ix ON edges (lts_access);

CREATE INDEX IF NOT EXISTS edges_geom_ix ON edges USING GIST (geometry);

CREATE INDEX IF NOT EXISTS h3_geom_ix ON h3_grid USING GIST(geometry);

--SPLIT EDGES WITH HEXAGONS 
CREATE TABLE density.split_edges_h3 AS
SELECT
    DISTINCT (ST_Dump(ST_Split(e.geometry, s.geometry))) .geom AS geometry,
    e.id
FROM
    density.segmented_lines AS e
    JOIN h3_grid AS s ON ST_Intersects(e.geometry, s.geometry);

-- JOIN ADDITIONAL DATA TO SPLIT EDGES
CREATE TABLE h3_edges AS
SELECT
    s.id,
    s.geometry,
    e.bike_length,
    e.bikeinfra_both_sides,
    e.cycling_allowed,
    e.lts_access,
    e.car_traffic
FROM
    density.split_edges_h3 s
    JOIN edges e USING (id);

CREATE TABLE density.h3_buffer AS
SELECT
    hex_id,
    ST_Buffer(geometry, -0.001) AS geometry
FROM
    h3_grid;

CREATE INDEX IF NOT EXISTS h3_buffer_geom_ix ON density.h3_buffer USING GIST (geometry);

CREATE INDEX IF NOT EXISTS h3_edges_geom_ix ON h3_edges USING GIST (geometry);

ALTER TABLE
    h3_edges
ADD
    COLUMN IF NOT EXISTS h3_id VARCHAR DEFAULT NULL;

UPDATE
    h3_edges
SET
    h3_id = h.hex_id
FROM
    density.h3_buffer h
WHERE
    ST_Intersects(h3_edges.geometry, h.geometry);

-- RECOMPUTE BIKE INFRA LENGTH
UPDATE
    h3_edges
SET
    bike_length = CASE
        WHEN (
            bikeinfra_both_sides IS TRUE
            AND cycling_allowed IS TRUE
        ) THEN ST_Length(geometry) * 2
        WHEN (
            bikeinfra_both_sides IS FALSE
            AND cycling_allowed IS TRUE
        ) THEN ST_Length(geometry)
        ELSE NULL
    END;

CREATE TABLE IF NOT EXISTS density.density_h3 AS WITH lts_1 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_1_length,
        h3_id
    FROM
        h3_edges
    WHERE
        lts_access IN (1)
    GROUP BY
        h3_id
),
lts_2 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_2_length,
        h3_id
    FROM
        h3_edges
    WHERE
        lts_access IN (2)
    GROUP BY
        h3_id
),
lts_3 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_3_length,
        h3_id
    FROM
        h3_edges
    WHERE
        lts_access IN (3)
    GROUP BY
        h3_id
),
lts_4 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_4_length,
        h3_id
    FROM
        h3_edges
    WHERE
        lts_access IN (4)
    GROUP BY
        h3_id
),
lts_5 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_5_length,
        h3_id
    FROM
        h3_edges
    WHERE
        lts_access IN (5)
    GROUP BY
        h3_id
),
lts_6 AS (
    SELECT
        SUM(ST_Length(geometry)) / 1000 AS lts_6_length,
        h3_id
    FROM
        h3_edges
    WHERE
        lts_access IN (6)
    GROUP BY
        h3_id
),
lts_7 AS (
    SELECT
        SUM(ST_Length(geometry)) / 1000 AS lts_7_length,
        h3_id
    FROM
        h3_edges
    WHERE
        lts_access IN (7)
    GROUP BY
        h3_id
),
total_car AS (
    SELECT
        SUM(ST_Length(geometry)) / 1000 AS total_car_length,
        h3_id
    FROM
        h3_edges
    WHERE
        car_traffic IS TRUE
        AND lts_access IN (1, 2, 3, 4, 7)
    GROUP BY
        h3_id
)
SELECT
    h3_grid.hex_id,
    lts_1.lts_1_length,
    lts_2.lts_2_length,
    lts_3.lts_3_length,
    lts_4.lts_4_length,
    lts_5.lts_5_length,
    lts_6.lts_6_length,
    lts_7.lts_7_length,
    total_car.total_car_length,
    h3_grid.geometry
FROM
    h3_grid
    LEFT JOIN lts_1 ON h3_grid.hex_id = lts_1.h3_id
    LEFT JOIN lts_2 ON h3_grid.hex_id = lts_2.h3_id
    LEFT JOIN lts_3 ON h3_grid.hex_id = lts_3.h3_id
    LEFT JOIN lts_4 ON h3_grid.hex_id = lts_4.h3_id
    LEFT JOIN lts_5 ON h3_grid.hex_id = lts_5.h3_id
    LEFT JOIN lts_6 ON h3_grid.hex_id = lts_6.h3_id
    LEFT JOIN lts_7 ON h3_grid.hex_id = lts_7.h3_id
    LEFT JOIN total_car ON h3_grid.hex_id = total_car.h3_id;

ALTER TABLE
    density.density_h3
ADD
    COLUMN IF NOT EXISTS total_network_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_2_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_3_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_4_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_7_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_car_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_network_dens DOUBLE PRECISION DEFAULT NULL;

UPDATE
    density.density_h3
SET
    lts_1_length = 0
WHERE
    lts_1_length IS NULL;

UPDATE
    density.density_h3
SET
    lts_2_length = 0
WHERE
    lts_2_length IS NULL;

UPDATE
    density.density_h3
SET
    lts_3_length = 0
WHERE
    lts_3_length IS NULL;

UPDATE
    density.density_h3
SET
    lts_4_length = 0
WHERE
    lts_4_length IS NULL;

UPDATE
    density.density_h3
SET
    lts_7_length = 0
WHERE
    lts_7_length IS NULL;

UPDATE
    density.density_h3
SET
    total_network_length = lts_1_length + lts_2_length + lts_3_length + lts_4_length + lts_7_length;

UPDATE
    density.density_h3
SET
    lts_1_2_length = lts_1_length + lts_2_length,
    lts_1_3_length = lts_1_length + lts_2_length + lts_3_length,
    lts_1_4_length = lts_1_length + lts_2_length + lts_3_length + lts_4_length;

UPDATE
    density.density_h3
SET
    lts_1_dens = lts_1_length / (ST_Area(geometry) / 1000000),
    lts_2_dens = lts_2_length / (ST_Area(geometry) / 1000000),
    lts_3_dens = lts_3_length / (ST_Area(geometry) / 1000000),
    lts_4_dens = lts_4_length / (ST_Area(geometry) / 1000000),
    lts_7_dens = lts_7_length / (ST_Area(geometry) / 1000000),
    lts_1_2_dens = (lts_1_length + lts_2_length) / (ST_Area(geometry) / 1000000),
    lts_1_3_dens = (lts_1_length + lts_2_length + lts_3_length) / (ST_Area(geometry) / 1000000),
    lts_1_4_dens = (
        lts_1_length + lts_2_length + lts_3_length + lts_4_length
    ) / (ST_Area(geometry) / 1000000),
    total_car_dens = (total_car_length) / (ST_Area(geometry) / 1000000),
    total_network_dens = (total_network_length) / (ST_Area(geometry) / 1000000);

UPDATE
    density.density_h3
SET
    lts_1_dens = 0
WHERE
    lts_1_dens IS NULL;

UPDATE
    density.density_h3
SET
    lts_1_2_dens = 0
WHERE
    lts_1_2_dens IS NULL;

UPDATE
    density.density_h3
SET
    lts_1_3_dens = 0
WHERE
    lts_1_3_dens IS NULL;

UPDATE
    density.density_h3
SET
    lts_1_4_dens = 0
WHERE
    lts_1_4_dens IS NULL;

UPDATE
    density.density_h3
SET
    total_car_dens = 0
WHERE
    total_car_dens IS NULL;

-- CALCULATE RELATIVE LENGTH
ALTER TABLE
    density.density_h3
ADD
    COLUMN IF NOT EXISTS lts_1_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_7_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_car_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_2_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_3_length_rel DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_4_length_rel DOUBLE PRECISION DEFAULT NULL;

UPDATE
    density.density_h3
SET
    lts_1_length_rel = lts_1_length / total_network_length,
    lts_2_length_rel = lts_2_length / total_network_length,
    lts_3_length_rel = lts_3_length / total_network_length,
    lts_4_length_rel = lts_4_length / total_network_length,
    lts_1_2_length_rel = (lts_1_length + lts_2_length) / total_network_length,
    lts_1_3_length_rel = (lts_1_length + lts_2_length + lts_3_length) / total_network_length,
    lts_1_4_length_rel = (
        lts_1_length + lts_2_length + lts_3_length + lts_4_length
    ) / total_network_length,
    lts_7_length_rel = lts_7_length / total_network_length,
    total_car_length_rel = total_car_length / total_network_length
WHERE
    total_network_length > 0;

DO $$
DECLARE
    id_missing INT;

BEGIN
    SELECT
        COUNT(*) INTO id_missing
    FROM
        density.density_h3
    WHERE
        hex_id IS NULL;

ASSERT id_missing = 0,
'Areas missing id';

END $$;

DO $$
DECLARE
    miscalculated INT;

BEGIN
    SELECT
        COUNT(*) INTO miscalculated
    FROM
        density.density_h3
    WHERE
        lts_1_2_dens < lts_1_dens
        OR lts_1_3_dens < lts_1_2_dens
        OR lts_1_4_dens < lts_1_3_dens
        OR total_network_dens < lts_1_4_dens;

ASSERT miscalculated = 0,
'Problem with network density calculation. Check if the network density is calculated correctly.';

END $$;

DROP TABLE IF EXISTS density.split_edges_h3;

--DROP TABLE IF EXISTS h3_edges;
DROP TABLE IF EXISTS density.h3_buffer;

DROP TABLE IF EXISTS density.segmented_lines;