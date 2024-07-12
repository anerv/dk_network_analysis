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
    hex_grid;

CREATE INDEX IF NOT EXISTS centroid_geom_ix ON reach.centroids USING GIST (geometry);

ALTER TABLE
    reach.segment_nodes
ADD
    COLUMN IF NOT EXISTS hex_id VARCHAR;

UPDATE
    reach.segment_nodes
SET
    hex_id = hex_grid.hex_id
FROM
    hex_grid
WHERE
    ST_Intersects(reach.segment_nodes.geometry, hex_grid.geometry);

CREATE VIEW reach.nodes_all_view AS
SELECT
    DISTINCT node AS id
FROM
    (
        SELECT
            source AS node
        FROM
            reach.edge_segments
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
            reach.edge_segments
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
            reach.edge_segments
        WHERE
            lts_access IN (1)
            OR lts_1_gap IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            reach.edge_segments
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
            reach.edge_segments
        WHERE
            lts_access IN (1, 2)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
        UNION
        ALL
        SELECT
            target AS node
        FROM
            reach.edge_segments
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
            reach.edge_segments
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
            reach.edge_segments
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
            reach.edge_segments
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
            reach.edge_segments
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
            reach.edge_segments
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
            reach.edge_segments
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
    reach.segment_nodes
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
    reach.segment_nodes
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
    reach.segment_nodes
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
    reach.segment_nodes
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
    reach.segment_nodes
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
    reach.segment_nodes
WHERE
    id IN (
        SELECT
            id
        FROM
            reach.nodes_car_view
    );

-- TODO FILL BASED LARGEST COMPONENT SIZE FOR LTS 1 which node belongs to
ALTER TABLE
    reach.nodes_lts_1
ADD
    COLUMN component_size FLOAT DEFAULT NULL;

ALTER TABLE
    reach.nodes_lts_2
ADD
    COLUMN component_size FLOAT DEFAULT NULL;

ALTER TABLE
    reach.nodes_lts_3
ADD
    COLUMN component_size FLOAT DEFAULT NULL;

ALTER TABLE
    reach.nodes_lts_4
ADD
    COLUMN component_size FLOAT DEFAULT NULL;

ALTER TABLE
    reach.nodes_lts_car
ADD
    COLUMN component_size FLOAT DEFAULT NULL;

CREATE INDEX IF NOT EXISTS nodes_lts_1_hex_id_ix ON reach.nodes_lts_1 (id);

CREATE INDEX IF NOT EXISTS nodes_lts_2_hex_id_ix ON reach.nodes_lts_2 (id);

CREATE INDEX IF NOT EXISTS nodes_lts_3_hex_id_ix ON reach.nodes_lts_3 (id);

CREATE INDEX IF NOT EXISTS nodes_lts_4_hex_id_ix ON reach.nodes_lts_4 (id);

CREATE INDEX IF NOT EXISTS nodes_lts_car_hex_id_ix ON reach.nodes_lts_car (id);

WITH component_edges AS (
    SELECT
        source,
        target,
        component_size_1
    FROM
        reach.edge_segments
    WHERE
        component_size_1 IS NOT NULL
)
UPDATE
    reach.nodes_lts_1
SET
    component_size = ce.component_size_1
FROM
    component_edges ce
WHERE
    reach.nodes_lts_1.id = ce.source
    OR reach.nodes_lts_1.id = ce.target;

WITH component_edges AS (
    SELECT
        source,
        target,
        component_size_1_2
    FROM
        reach.edge_segments
    WHERE
        component_size_1_2 IS NOT NULL
)
UPDATE
    reach.nodes_lts_2
SET
    component_size = ce.component_size_1_2
FROM
    component_edges ce
WHERE
    reach.nodes_lts_2.id = ce.source
    OR reach.nodes_lts_2.id = ce.target;

WITH component_edges AS (
    SELECT
        source,
        target,
        component_size_1_3
    FROM
        reach.edge_segments
    WHERE
        component_size_1_3 IS NOT NULL
)
UPDATE
    reach.nodes_lts_3
SET
    component_size = ce.component_size_1_3
FROM
    component_edges ce
WHERE
    reach.nodes_lts_3.id = ce.source
    OR reach.nodes_lts_3.id = ce.target;

WITH component_edges AS (
    SELECT
        source,
        target,
        component_size_1_4
    FROM
        reach.edge_segments
    WHERE
        component_size_1_4 IS NOT NULL
)
UPDATE
    reach.nodes_lts_4
SET
    component_size = ce.component_size_1_4
FROM
    component_edges ce
WHERE
    reach.nodes_lts_4.id = ce.source
    OR reach.nodes_lts_4.id = ce.target;

WITH component_edges AS (
    SELECT
        source,
        target,
        component_size_car
    FROM
        reach.edge_segments
    WHERE
        component_size_car IS NOT NULL
)
UPDATE
    reach.nodes_lts_car
SET
    component_size = ce.component_size_car
FROM
    component_edges ce
WHERE
    reach.nodes_lts_car.id = ce.source
    OR reach.nodes_lts_car.id = ce.target;

CREATE TABLE reach.hex_lts_1 AS WITH joined_points AS (
    SELECT
        ce.hex_id AS hex_id,
        n.id AS node_id,
        ce.geometry AS hex_centroid,
        n.geometry AS node_geom,
        n.component_size AS component_size,
        ROW_NUMBER() OVER (
            PARTITION BY ce.hex_id
            ORDER BY
                component_size DESC,
                ST_Distance(ce.geometry, n.geometry)
        ) AS rn
    FROM
        reach.centroids ce
        JOIN reach.nodes_lts_1 n ON ce.hex_id = n.hex_id
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
                component_size DESC,
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
                component_size DESC,
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
                component_size DESC,
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
                component_size DESC,
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