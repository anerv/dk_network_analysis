DROP TABLE IF EXISTS reach.centroids;

DROP TABLE IF EXISTS reach.nodes_all;

DROP TABLE IF EXISTS reach.nodes_lts_1;

DROP TABLE IF EXISTS reach.nodes_lts_2;

DROP TABLE IF EXISTS reach.nodes_lts_3;

DROP TABLE IF EXISTS reach.nodes_lts_4;

DROP TABLE IF EXISTS reach.nodes_lts_car;

DROP VIEW IF EXISTS reach.nodes_all_view;

DROP VIEW IF EXISTS reach.nodes_lts_1_view;

DROP VIEW IF EXISTS reach.nodes_lts_2_view;

DROP VIEW IF EXISTS reach.nodes_lts_3_view;

DROP VIEW IF EXISTS reach.nodes_lts_4_view;

DROP VIEW IF EXISTS reach.nodes_car_view;

DROP TABLE IF EXISTS reach.hex_lts_1;

DROP TABLE IF EXISTS reach.hex_lts_2;

DROP TABLE IF EXISTS reach.hex_lts_3;

DROP TABLE IF EXISTS reach.hex_lts_4;

DROP TABLE IF EXISTS reach.hex_car;

-- ***** Find closest node to each hex centroid for all LTS levels *****
CREATE TABLE reach.centroids AS
SELECT
    ST_Centroid(geometry) AS geometry,
    hex_id
FROM
    h3_grid;

CREATE INDEX IF NOT EXISTS centroid_geom_ix ON reach.centroids USING GIST (geometry);

ALTER TABLE
    nodes
ADD
    COLUMN IF NOT EXISTS hex_id VARCHAR;

UPDATE
    nodes
SET
    hex_id = h3_grid.hex_id
FROM
    h3_grid
WHERE
    ST_Intersects(nodes.geometry, h3_grid.geometry);

CREATE VIEW reach.nodes_all_view AS
SELECT
    DISTINCT node AS id
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2, 3, 4, 7)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
            OR lts_4_gap IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2, 3, 4, 7)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
            OR lts_4_gap IS TRUE
    ) AS nodes;

CREATE VIEW reach.nodes_lts_1_view AS
SELECT
    DISTINCT node AS id
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts_access IN (1)
            OR lts_1_gap IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts_access IN (1)
            OR lts_1_gap IS TRUE
    ) AS nodes;

CREATE VIEW reach.nodes_lts_2_view AS
SELECT
    DISTINCT node AS id
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
    ) AS nodes;

CREATE VIEW reach.nodes_lts_3_view AS
SELECT
    DISTINCT node AS id
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2, 3)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2, 3)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
    ) AS nodes;

CREATE VIEW reach.nodes_lts_4_view AS
SELECT
    DISTINCT node AS id
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2, 3, 4)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
            OR lts_4_gap IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts_access IN (1, 2, 3, 4)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
            OR lts_4_gap IS TRUE
    ) AS nodes;

CREATE VIEW reach.nodes_car_view AS
SELECT
    DISTINCT node AS id
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            (
                lts_access IN (1, 2, 3, 4, 7)
                OR lts_1_gap IS TRUE
                OR lts_2_gap IS TRUE
                OR lts_3_gap IS TRUE
                OR lts_4_gap IS TRUE
            )
            AND car_traffic IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            (
                lts_access IN (1, 2, 3, 4, 7)
                OR lts_1_gap IS TRUE
                OR lts_2_gap IS TRUE
                OR lts_3_gap IS TRUE
                OR lts_4_gap IS TRUE
            )
            AND car_traffic IS TRUE
    ) AS nodes;

CREATE TABLE reach.nodes_all AS
SELECT
    id,
    geometry,
    hex_id
FROM
    nodes
WHERE
    id IN (
        SELECT
            id
        FROM
            reach.nodes_all_view
    );

CREATE TABLE reach.nodes_lts_1 AS
SELECT
    id,
    geometry,
    hex_id
FROM
    nodes
WHERE
    id IN (
        SELECT
            id
        FROM
            reach.nodes_lts_1_view
    );

CREATE TABLE reach.nodes_lts_2 AS
SELECT
    id,
    geometry,
    hex_id
FROM
    nodes
WHERE
    id IN (
        SELECT
            id
        FROM
            reach.nodes_lts_2_view
    );

CREATE TABLE reach.nodes_lts_3 AS
SELECT
    id,
    geometry,
    hex_id
FROM
    nodes
WHERE
    id IN (
        SELECT
            id
        FROM
            reach.nodes_lts_3_view
    );

CREATE TABLE reach.nodes_lts_4 AS
SELECT
    id,
    geometry,
    hex_id
FROM
    nodes
WHERE
    id IN (
        SELECT
            id
        FROM
            reach.nodes_lts_4_view
    );

CREATE TABLE reach.nodes_lts_car AS
SELECT
    id,
    geometry,
    hex_id
FROM
    nodes
WHERE
    id IN (
        SELECT
            id
        FROM
            reach.nodes_car_view
    );

CREATE TABLE reach.hex_lts_1 AS WITH joined_points AS (
    SELECT
        ce.hex_id AS hex_id,
        b.id AS node_id,
        ce.geometry AS hex_centroid,
        b.geometry AS node_geom,
        ROW_NUMBER() OVER (
            PARTITION BY ce.hex_id
            ORDER BY
                ST_Distance(ce.geometry, b.geometry)
        ) AS rn
    FROM
        reach.centroids ce
        JOIN reach.nodes_lts_1 b ON ce.hex_id = b.hex_id
)
SELECT
    hex_id,
    node_id,
    hex_centroid,
    node_geom
FROM
    joined_points
WHERE
    rn = 1;

CREATE TABLE reach.hex_lts_2 AS WITH joined_points AS (
    SELECT
        ce.hex_id AS hex_id,
        b.id AS node_id,
        ce.geometry AS hex_centroid,
        b.geometry AS node_geom,
        ROW_NUMBER() OVER (
            PARTITION BY ce.hex_id
            ORDER BY
                ST_Distance(ce.geometry, b.geometry)
        ) AS rn
    FROM
        reach.centroids ce
        JOIN reach.nodes_lts_2 b ON ce.hex_id = b.hex_id
)
SELECT
    hex_id,
    node_id,
    hex_centroid,
    node_geom
FROM
    joined_points
WHERE
    rn = 1;

CREATE TABLE reach.hex_lts_3 AS WITH joined_points AS (
    SELECT
        ce.hex_id AS hex_id,
        b.id AS node_id,
        ce.geometry AS hex_centroid,
        b.geometry AS node_geom,
        ROW_NUMBER() OVER (
            PARTITION BY ce.hex_id
            ORDER BY
                ST_Distance(ce.geometry, b.geometry)
        ) AS rn
    FROM
        reach.centroids ce
        JOIN reach.nodes_lts_3 b ON ce.hex_id = b.hex_id
)
SELECT
    hex_id,
    node_id,
    hex_centroid,
    node_geom
FROM
    joined_points
WHERE
    rn = 1;

CREATE TABLE reach.hex_lts_4 AS WITH joined_points AS (
    SELECT
        ce.hex_id AS hex_id,
        b.id AS node_id,
        ce.geometry AS hex_centroid,
        b.geometry AS node_geom,
        ROW_NUMBER() OVER (
            PARTITION BY ce.hex_id
            ORDER BY
                ST_Distance(ce.geometry, b.geometry)
        ) AS rn
    FROM
        reach.centroids ce
        JOIN reach.nodes_lts_4 b ON ce.hex_id = b.hex_id
)
SELECT
    hex_id,
    node_id,
    hex_centroid,
    node_geom
FROM
    joined_points
WHERE
    rn = 1;

CREATE TABLE reach.hex_car AS WITH joined_points AS (
    SELECT
        ce.hex_id AS hex_id,
        b.id AS node_id,
        ce.geometry AS hex_centroid,
        b.geometry AS node_geom,
        ROW_NUMBER() OVER (
            PARTITION BY ce.hex_id
            ORDER BY
                ST_Distance(ce.geometry, b.geometry)
        ) AS rn
    FROM
        reach.centroids ce
        JOIN reach.nodes_lts_car b ON ce.hex_id = b.hex_id
)
SELECT
    hex_id,
    node_id,
    hex_centroid,
    node_geom
FROM
    joined_points
WHERE
    rn = 1;

-- drop unneccesary/intermediate tables
DROP TABLE IF EXISTS reach.centroids;

DROP TABLE IF EXISTS reach.nodes_all;

DROP TABLE IF EXISTS reach.nodes_lts_1;

DROP TABLE IF EXISTS reach.nodes_lts_2;

DROP TABLE IF EXISTS reach.nodes_lts_3;

DROP TABLE IF EXISTS reach.nodes_lts_4;

DROP TABLE IF EXISTS reach.nodes_lts_car;