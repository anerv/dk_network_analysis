DROP TABLE IF EXISTS fragmentation.component_edges;

DROP TABLE IF EXISTS fragmentation.component_size_all;

DROP TABLE IF EXISTS fragmentation.component_size_1;

DROP TABLE IF EXISTS fragmentation.component_size_2;

DROP TABLE IF EXISTS fragmentation.component_size_3;

DROP TABLE IF EXISTS fragmentation.component_size_4;

DROP TABLE IF EXISTS fragmentation.component_size_car;

CREATE TABLE fragmentation.component_edges AS
SELECT
    id,
    highway,
    bike_length,
    municipality,
    component_all,
    component_1,
    component_1_2,
    component_1_3,
    component_1_4,
    component_car,
    geometry
FROM
    edges
WHERE
    component_all IS NOT NULL;

UPDATE
    fragmentation.component_edges
SET
    bike_length = ST_Length(geometry)
WHERE
    bike_length IS NULL;

CREATE TABLE fragmentation.component_size_all AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ST_Buffer(ST_ConcaveHull(ST_Collect(geometry), 0.2), 5) AS buffer_geom,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        fragmentation.component_edges
    WHERE
        component_all IS NOT NULL
    GROUP BY
        component_all
);

CREATE TABLE fragmentation.component_size_1 AS (
    SELECT
        COUNT(id),
        component_1,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ST_Buffer(ST_ConcaveHull(ST_Collect(geometry), 0.2), 5) AS buffer_geom,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        fragmentation.component_edges
    WHERE
        component_1 IS NOT NULL
    GROUP BY
        component_1
);

CREATE TABLE fragmentation.component_size_2 AS (
    SELECT
        COUNT(id),
        component_1_2,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ST_Buffer(ST_ConcaveHull(ST_Collect(geometry), 0.2), 5) AS buffer_geom,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        fragmentation.component_edges
    WHERE
        component_1_2 IS NOT NULL
    GROUP BY
        component_1_2
);

CREATE TABLE fragmentation.component_size_3 AS (
    SELECT
        COUNT(id),
        component_1_3,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ST_Buffer(ST_ConcaveHull(ST_Collect(geometry), 0.2), 5) AS buffer_geom,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        fragmentation.component_edges
    WHERE
        component_1_3 IS NOT NULL
    GROUP BY
        component_1_3
);

CREATE TABLE fragmentation.component_size_4 AS (
    SELECT
        COUNT(id),
        component_1_4,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ST_Buffer(ST_ConcaveHull(ST_Collect(geometry), 0.2), 5) AS buffer_geom,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        fragmentation.component_edges
    WHERE
        component_1_4 IS NOT NULL
    GROUP BY
        component_1_4
);

CREATE TABLE fragmentation.component_size_car AS (
    SELECT
        COUNT(id),
        component_car,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ST_Buffer(ST_ConcaveHull(ST_Collect(geometry), 0.2), 5) AS buffer_geom,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        fragmentation.component_edges
    WHERE
        component_car IS NOT NULL
    GROUP BY
        component_car
);

ALTER TABLE
    fragmentation.component_size_all
ADD
    COLUMN IF NOT EXISTS buffer_area DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_size_1
ADD
    COLUMN IF NOT EXISTS buffer_area DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_size_2
ADD
    COLUMN IF NOT EXISTS buffer_area DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_size_3
ADD
    COLUMN IF NOT EXISTS buffer_area DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_size_4
ADD
    COLUMN IF NOT EXISTS buffer_area DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_size_car
ADD
    COLUMN IF NOT EXISTS buffer_area DOUBLE PRECISION;

UPDATE
    fragmentation.component_size_all
SET
    buffer_area = ST_Area(buffer_geom);

UPDATE
    fragmentation.component_size_1
SET
    buffer_area = ST_Area(buffer_geom);

UPDATE
    fragmentation.component_size_2
SET
    buffer_area = ST_Area(buffer_geom);

UPDATE
    fragmentation.component_size_3
SET
    buffer_area = ST_Area(buffer_geom);

UPDATE
    fragmentation.component_size_4
SET
    buffer_area = ST_Area(buffer_geom);

UPDATE
    fragmentation.component_size_car
SET
    buffer_area = ST_Area(buffer_geom);