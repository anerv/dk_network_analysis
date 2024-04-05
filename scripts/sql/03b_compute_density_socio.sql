DROP TABLE IF EXISTS density_socio;

DROP TABLE IF EXISTS split_edges;

DROP TABLE IF EXISTS socio_edges;

DROP TABLE IF EXISTS socio_buffer;

CREATE INDEX IF NOT EXISTS lts_access_ix ON edges (lts_access);

CREATE INDEX IF NOT EXISTS edges_geom_ix ON edges USING GIST (geometry);

-- SPLIT EDGES WITH VOTING AREAS
CREATE TABLE split_edges AS
SELECT
    DISTINCT (ST_Dump(ST_Split(e.geometry, s.geometry))) .geom AS geometry,
    e.id
FROM
    edges AS e
    JOIN socio AS s ON ST_Intersects(e.geometry, s.geometry);

-- JOIN ADDITIONAL DATA TO SPLIT EDGES
CREATE TABLE socio_edges AS
SELECT
    s.id,
    s.geometry,
    e.bike_length,
    e.bikeinfra_both_sides,
    e.cycling_allowed,
    e.lts_access,
    e.car_traffic
FROM
    split_edges s
    JOIN edges e USING (id);

CREATE TABLE socio_buffer AS
SELECT
    id,
    ST_Buffer(geometry, -1) AS geometry
FROM
    socio;

CREATE INDEX IF NOT EXISTS socio_buffer_geom_ix ON socio_buffer USING GIST (geometry);

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
    socio_buffer s
WHERE
    ST_Intersects(socio_edges.geometry, s.geometry);

-- RECOMPUTE BIKE INFRA LENGTH
UPDATE
    socio_edges
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

CREATE TABLE IF NOT EXISTS density_socio AS WITH lts_1 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_1_length,
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
        SUM(bike_length) / 1000 AS lts_2_length,
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
        SUM(bike_length) / 1000 AS lts_3_length,
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
        SUM(bike_length) / 1000 AS lts_4_length,
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
        SUM(bike_length) / 1000 AS lts_5_length,
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
        SUM(ST_Length(geometry)) / 1000 AS lts_6_length,
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
        SUM(ST_Length(geometry)) / 1000 AS lts_7_length,
        socio_id
    FROM
        socio_edges
    WHERE
        lts_access IN (7)
    GROUP BY
        socio_id
),
total_car AS (
    SELECT
        SUM(ST_Length(geometry)) / 1000 AS total_car,
        socio_id
    FROM
        socio_edges
    WHERE
        car_traffic IS TRUE
    GROUP BY
        socio_id
)
SELECT
    lts_1.socio_id,
    lts_1.lts_1_length,
    lts_2.lts_2_length,
    lts_3.lts_3_length,
    lts_4.lts_4_length,
    lts_5.lts_5_length,
    lts_6.lts_6_length,
    lts_7.lts_7_length,
    total_car.total_car,
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
    density_socio
ADD
    COLUMN IF NOT EXISTS lts_1_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_car_dens DOUBLE PRECISION DEFAULT NULL;

UPDATE
    density_socio
SET
    lts_1_length = 0
WHERE
    lts_1_length IS NULL;

UPDATE
    density_socio
SET
    lts_2_length = 0
WHERE
    lts_2_length IS NULL;

UPDATE
    density_socio
SET
    lts_3_length = 0
WHERE
    lts_3_length IS NULL;

UPDATE
    density_socio
SET
    lts_4_length = 0
WHERE
    lts_4_length IS NULL;

UPDATE
    density_socio
SET
    lts_1_dens = lts_1_length / (ST_Area(geometry) / 1000000),
    lts_1_2_dens = (lts_1_length + lts_2_length) / (ST_Area(geometry) / 1000000),
    lts_1_3_dens = (lts_1_length + lts_2_length + lts_3_length) / (ST_Area(geometry) / 1000000),
    lts_1_4_dens = (
        lts_1_length + lts_2_length + lts_3_length + lts_4_length
    ) / (ST_Area(geometry) / 1000000),
    total_car_dens = (total_car) / (ST_Area(geometry) / 1000000);

UPDATE
    density_socio
SET
    lts_1_dens = 0
WHERE
    lts_1_dens IS NULL;

UPDATE
    density_socio
SET
    lts_1_2_dens = 0
WHERE
    lts_1_2_dens IS NULL;

UPDATE
    density_socio
SET
    lts_1_3_dens = 0
WHERE
    lts_1_3_dens IS NULL;

UPDATE
    density_socio
SET
    lts_1_4_dens = 0
WHERE
    lts_1_4_dens IS NULL;

UPDATE
    density_socio
SET
    total_car_dens = 0
WHERE
    total_car_dens IS NULL;

DROP TABLE IF EXISTS split_edges;

DROP TABLE IF EXISTS socio_edges;

DROP TABLE IF EXISTS socio_buffer;