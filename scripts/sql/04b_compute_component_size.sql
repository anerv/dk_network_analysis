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
    source,
    target,
    highway,
    infra_length,
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

CREATE TABLE fragmentation.component_size_all AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) / 1000 AS geom_length,
        SUM(infra_length) / 1000 AS infra_length,
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
        SUM(ST_Length(geometry)) / 1000 AS geom_length,
        SUM(infra_length) / 1000 AS infra_length,
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
        SUM(ST_Length(geometry)) / 1000 AS geom_length,
        SUM(infra_length) / 1000 AS infra_length,
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
        SUM(ST_Length(geometry)) / 1000 AS geom_length,
        SUM(infra_length) / 1000 AS infra_length,
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
        SUM(ST_Length(geometry)) / 1000 AS geom_length,
        SUM(infra_length) / 1000 AS infra_length,
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
        SUM(ST_Length(geometry)) / 1000 AS geom_length,
        SUM(infra_length) / 1000 AS infra_length,
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
    buffer_area = ST_Area(buffer_geom) / 1000000;

UPDATE
    fragmentation.component_size_2
SET
    buffer_area = ST_Area(buffer_geom) / 1000000;

UPDATE
    fragmentation.component_size_3
SET
    buffer_area = ST_Area(buffer_geom) / 1000000;

UPDATE
    fragmentation.component_size_4
SET
    buffer_area = ST_Area(buffer_geom) / 1000000;

UPDATE
    fragmentation.component_size_car
SET
    buffer_area = ST_Area(buffer_geom) / 1000000;

-- ADD COMPONENT SIZE TO COMPONENT EDGES (for later use)
ALTER TABLE
    fragmentation.component_edges
ADD
    COLUMN IF NOT EXISTS component_size_1 DECIMAL,
ADD
    COLUMN IF NOT EXISTS component_size_1_2 DECIMAL,
ADD
    COLUMN IF NOT EXISTS component_size_1_3 DECIMAL,
ADD
    COLUMN IF NOT EXISTS component_size_1_4 DECIMAL,
ADD
    COLUMN IF NOT EXISTS component_size_car DECIMAL;

UPDATE
    fragmentation.component_edges
SET
    component_size_1 = component_size_1.infra_length
FROM
    fragmentation.component_size_1
WHERE
    fragmentation.component_edges.component_1 = fragmentation.component_size_1.component_1;

UPDATE
    fragmentation.component_edges
SET
    component_size_1_2 = component_size_2.infra_length
FROM
    fragmentation.component_size_2
WHERE
    fragmentation.component_edges.component_1_2 = fragmentation.component_size_2.component_1_2;

UPDATE
    fragmentation.component_edges
SET
    component_size_1_3 = component_size_3.infra_length
FROM
    fragmentation.component_size_3
WHERE
    fragmentation.component_edges.component_1_3 = fragmentation.component_size_3.component_1_3;

UPDATE
    fragmentation.component_edges
SET
    component_size_1_4 = component_size_4.infra_length
FROM
    fragmentation.component_size_4
WHERE
    fragmentation.component_edges.component_1_4 = fragmentation.component_size_4.component_1_4;

UPDATE
    fragmentation.component_edges
SET
    component_size_car = component_size_car.infra_length
FROM
    fragmentation.component_size_car
WHERE
    fragmentation.component_edges.component_car = fragmentation.component_size_car.component_car;