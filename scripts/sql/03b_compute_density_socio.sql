DROP TABLE IF EXISTS density.density_socio;

DROP TABLE IF EXISTS density.split_edges_socio;

DROP TABLE IF EXISTS socio_edges;

DROP TABLE IF EXISTS density.socio_buffer;

DROP TABLE IF EXISTS density.socio_buffer_100;

DROP TABLE IF EXISTS density.segmented_lines;

CREATE INDEX IF NOT EXISTS lts_access_ix ON edges (lts_access);

CREATE INDEX IF NOT EXISTS edges_geom_ix ON edges USING GIST (geometry);

--SUBDIVIDE EDGES TO MAKE SURE THEY ARE ONLY INTERSECTING ONE AREA/HEXAGON
WITH segs(id, geometry) AS (
    SELECT
        id,
        geometry
    FROM
        edges
)
SELECT
    ROW_NUMBER () OVER () AS row_number,
    id,
    ST_LineSubstring(geometry, startfrac, LEAST(endfrac, 1)) AS geometry INTO density.segmented_lines
FROM
    (
        SELECT
            id,
            geometry,
            ST_Length(geometry) len,
            200 sublen
        FROM
            segs
    ) AS d
    CROSS JOIN LATERAL (
        SELECT
            i,
            (sublen * i) / len AS startfrac,
            (sublen * (i + 1)) / len AS endfrac
        FROM
            generate_series(0, floor(len / sublen) :: INTEGER) AS t(i)
        WHERE
            (sublen * i) / len <> 1.0
    ) AS d2;

DELETE FROM
    density.segmented_lines
WHERE
    ST_GeometryType(geometry) = 'ST_Point';

-- SPLIT EDGES WITH VOTING AREAS
CREATE TABLE density.split_edges_socio AS
SELECT
    DISTINCT (ST_Dump(ST_Split(e.geometry, s.geometry))) .geom AS geometry,
    e.id
FROM
    density.segmented_lines AS e
    JOIN socio AS s ON ST_Intersects(e.geometry, s.geometry);

-- JOIN ADDITIONAL DATA TO SPLIT EDGES
CREATE TABLE socio_edges AS
SELECT
    s.id,
    s.geometry,
    e.infra_length,
    e.bikeinfra_both_sides,
    e.cycling_allowed,
    e.lts_access,
    e.car_traffic
FROM
    density.split_edges_socio s
    JOIN edges e USING (id);

CREATE TABLE density.socio_buffer AS
SELECT
    id,
    ST_Buffer(geometry, -0.001) AS geometry
FROM
    socio;

CREATE TABLE density.socio_buffer_100 AS
SELECT
    id,
    ST_Buffer(geometry, 100) AS geometry
FROM
    socio;

CREATE INDEX IF NOT EXISTS socio_buffer_geom_ix ON density.socio_buffer USING GIST (geometry);

CREATE INDEX IF NOT EXISTS socio_buffer100_geom_ix ON density.socio_buffer_100 USING GIST (geometry);

CREATE INDEX IF NOT EXISTS socio_edges_geom_ix ON socio_edges USING GIST (geometry);

ALTER TABLE
    socio_edges
ADD
    COLUMN IF NOT EXISTS socio_id BIGINT DEFAULT NULL;

UPDATE
    socio_edges
SET
    socio_id = s.id
FROM
    density.socio_buffer s
WHERE
    ST_Intersects(socio_edges.geometry, s.geometry);

UPDATE
    socio_edges
SET
    socio_id = s.id
FROM
    density.socio_buffer_100 s
WHERE
    ST_Intersects(socio_edges.geometry, s.geometry)
    AND socio_id IS NULL;

-- RECOMPUTE INFRA LENGTH
UPDATE
    socio_edges
SET
    infra_length = ST_Length(geometry);

CREATE TABLE IF NOT EXISTS density.density_socio AS WITH lts_1 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_1_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (1)
    GROUP BY
        socio_id
),
lts_2 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_2_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (2)
    GROUP BY
        socio_id
),
lts_3 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_3_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (3)
    GROUP BY
        socio_id
),
lts_4 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_4_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (4)
    GROUP BY
        socio_id
),
lts_5 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_5_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (5)
    GROUP BY
        socio_id
),
lts_6 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_6_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (6)
    GROUP BY
        socio_id
),
lts_7 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_7_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (7)
    GROUP BY
        socio_id
),
lts_8 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_8_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (8)
    GROUP BY
        municipality
),
total_car AS (
    SELECT
        SUM(infra_length) / 1000 AS total_car_length,
        socio_id
    FROM
        socio_edges
    WHERE
        car_traffic IS TRUE
        AND lts_access IN (1, 2, 3, 4, 7)
    GROUP BY
        socio_id
)
SELECT
    socio.id,
    lts_1.lts_1_length,
    lts_2.lts_2_length,
    lts_3.lts_3_length,
    lts_4.lts_4_length,
    lts_5.lts_5_length,
    lts_6.lts_6_length,
    lts_7.lts_7_length,
    total_car.total_car_length,
    socio.geometry
FROM
    socio
    LEFT JOIN lts_1 ON socio.id = lts_1.socio_id
    LEFT JOIN lts_2 ON socio.id = lts_2.socio_id
    LEFT JOIN lts_3 ON socio.id = lts_3.socio_id
    LEFT JOIN lts_4 ON socio.id = lts_4.socio_id
    LEFT JOIN lts_5 ON socio.id = lts_5.socio_id
    LEFT JOIN lts_6 ON socio.id = lts_6.socio_id
    LEFT JOIN lts_7 ON socio.id = lts_7.socio_id
    LEFT JOIN total_car ON socio.id = total_car.socio_id;

ALTER TABLE
    density.density_socio
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
    density.density_socio
SET
    lts_1_length = 0
WHERE
    lts_1_length IS NULL;

UPDATE
    density.density_socio
SET
    lts_2_length = 0
WHERE
    lts_2_length IS NULL;

UPDATE
    density.density_socio
SET
    lts_3_length = 0
WHERE
    lts_3_length IS NULL;

UPDATE
    density.density_socio
SET
    lts_4_length = 0
WHERE
    lts_4_length IS NULL;

UPDATE
    density.density_socio
SET
    lts_7_length = 0
WHERE
    lts_7_length IS NULL;

UPDATE
    density.density_socio
SET
    total_network_length = lts_1_length + lts_2_length + lts_3_length + lts_4_length + lts_7_length;

UPDATE
    density.density_socio
SET
    lts_1_2_length = lts_1_length + lts_2_length,
    lts_1_3_length = lts_1_length + lts_2_length + lts_3_length,
    lts_1_4_length = lts_1_length + lts_2_length + lts_3_length + lts_4_length;

UPDATE
    density.density_socio
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
    density.density_socio
SET
    lts_1_dens = 0
WHERE
    lts_1_dens IS NULL;

UPDATE
    density.density_socio
SET
    lts_1_2_dens = 0
WHERE
    lts_1_2_dens IS NULL;

UPDATE
    density.density_socio
SET
    lts_1_3_dens = 0
WHERE
    lts_1_3_dens IS NULL;

UPDATE
    density.density_socio
SET
    lts_1_4_dens = 0
WHERE
    lts_1_4_dens IS NULL;

UPDATE
    density.density_socio
SET
    total_car_dens = 0
WHERE
    total_car_dens IS NULL;

-- CALCULATE RELATIVE LENGTH
ALTER TABLE
    density.density_socio
ADD
    COLUMN IF NOT EXISTS lts_1_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_7_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_car_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_2_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_3_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_4_pct DOUBLE PRECISION DEFAULT NULL;

UPDATE
    density.density_socio
SET
    lts_1_pct = lts_1_length / total_network_length * 100,
    lts_2_pct = lts_2_length / total_network_length * 100,
    lts_3_pct = lts_3_length / total_network_length * 100,
    lts_4_pct = lts_4_length / total_network_length * 100,
    lts_1_2_pct = (lts_1_length + lts_2_length) / total_network_length * 100,
    lts_1_3_pct = (lts_1_length + lts_2_length + lts_3_length) / total_network_length * 100,
    lts_1_4_pct = (
        lts_1_length + lts_2_length + lts_3_length + lts_4_length
    ) / total_network_length * 100,
    lts_7_pct = lts_7_length / total_network_length * 100,
    total_car_pct = total_car_length / total_network_length * 100
WHERE
    total_network_length > 0;

DO $$
DECLARE
    id_missing INT;

BEGIN
    SELECT
        COUNT(*) INTO id_missing
    FROM
        density.density_socio
    WHERE
        id IS NULL;

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
        density.density_socio
    WHERE
        lts_1_2_dens < lts_1_dens
        OR lts_1_3_dens < lts_1_2_dens
        OR lts_1_4_dens < lts_1_3_dens
        OR total_network_dens < lts_1_4_dens;

ASSERT miscalculated = 0,
'Problem with network density calculation. Check if the network density is calculated correctly.';

END $$;

DROP TABLE IF EXISTS density.split_edges_socio;

--DROP TABLE IF EXISTS socio_edges;
DROP TABLE IF EXISTS density.socio_buffer;

DROP TABLE IF EXISTS density.socio_buffer_100;