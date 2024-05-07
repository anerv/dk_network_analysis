DROP TABLE IF EXISTS centroids;

DROP TABLE IF EXISTS node_lts_1;

DROP TABLE IF EXISTS node_lts_2;

DROP TABLE IF EXISTS node_lts_3;

DROP TABLE IF EXISTS node_lts_4;

DROP TABLE IF EXISTS node_lts_car;

CREATE TABLE centroids AS
SELECT
    ST_Centroid(geometry) AS geometry,
    hex_id
FROM
    h3_grid;

CREATE INDEX IF NOT EXISTS centroid_geom_ix ON centroids USING GIST (geometry);

ALTER TABLE
    nodes
ADD
    COLUMN hex_id VARCHAR;

UPDATE
    nodes
SET
    hex_id = h3_grid.hex_id
WHERE
    ST_Intersects(nodes.geometry, h3_grid.geometry);

-- ALTER TABLE
--     nodes
-- ADD
--     COLUMN lts_access INT DEFAULT NULL;
-- UPDATE
--     nodes n
-- SET
--     lts_access = e.lts_access
CREATE TABLE node_lts_1 AS (
    SELECT
        source AS node,
        geometry
    UNION
    SELECT
        target AS node,
        geometry
    FROM
        edges
    WHERE
        lts_access = 1
);

CREATE TABLE node_lts_2 AS (
    SELECT
        source AS node,
        geometry
    UNION
    SELECT
        target AS node,
        geometry
    FROM
        edges
    WHERE
        lts_access IN (1, 2)
);

CREATE TABLE node_lts_3 AS (
    SELECT
        source AS node,
        geometry
    UNION
    SELECT
        target AS node,
        geometry
    FROM
        edges
    WHERE
        lts_access IN (1, 2, 3)
);

CREATE TABLE node_lts_4 AS (
    SELECT
        source AS node,
        geometry
    UNION
    SELECT
        target AS node,
        geometry
    FROM
        edges
    WHERE
        lts_access IN (1, 2, 3, 4)
);

CREATE TABLE node_lts_car AS (
    SELECT
        source AS node,
        geometry
    UNION
    SELECT
        target AS node,
        geometry
    FROM
        edges
    WHERE
        car_traffic IS TRUE
        AND lts_access IN (1, 2, 3, 4, 7)
);

CREATE INDEX IF NOT EXISTS node1_geom_ix ON nodes_lts_1 USING GIST (geometry);

CREATE INDEX IF NOT EXISTS node2_geom_ix ON nodes_lts_2 USING GIST (geometry);

CREATE INDEX IF NOT EXISTS node3_geom_ix ON nodes_lts_3 USING GIST (geometry);

CREATE INDEX IF NOT EXISTS node4_geom_ix ON nodes_lts_4 USING GIST (geometry);

CREATE INDEX IF NOT EXISTS nodecar_geom_ix ON nodes_lts_car USING GIST (geometry);

-- JOIN centroids to nodes 1 on hex id limit 1 order by distance
SELECT
    ce.hex_id,
    n.node,
    n.geometry,
    ST_Distance(ce.geometry, n.geometry) AS dist
FROM
    centroids ce
    JOIN LATERAL lts_nodes_1 n ON ce.hex_id = n.hex_id
ORDER BY
    dist
LIMIT
    1;

SELECT
    ce.hex_id,
    n.node,
    n.geometry,
    ST_Distance(ce.geometry, n.geometry) AS dist
FROM
    centroids ce
    JOIN LATERAL lts_nodes_1 n ON ce.hex_id = n.hex_id;

SELECT
    subways.gid AS subway_gid,
    subways.name AS subway,
    streets.name AS street,
    streets.gid AS street_gid,
    streets.geom :: geometry(MultiLinestring, 26918) AS street_geom,
    streets.dist
FROM
    nyc_subway_stations subways
    CROSS JOIN LATERAL (
        SELECT
            streets.name,
            streets.geom,
            streets.gid,
            streets.geom < -> subways.geom AS dist
        FROM
            nyc_streets AS streets
        ORDER BY
            dist
        LIMIT
            1
    ) streets;

SELECT
    A .id,
    b.value,
    -- ST_Distance(a.wkb_geometry::GEOGRAPHY, b.wkb_geometry::GEOGRAPHY) as dist,
    A .wkb_geometry
FROM
    t2 AS A
    JOIN LATERAL (
        SELECT
            VALUE
        FROM
            t1
        ORDER BY
            A .wkb_geometry < -> t2.wkb_geometry
        LIMIT
            1
    ) AS b ON TRUE -- CREATE JOINS BETWEEN hex centroids AND edge nodes for each lts
    -- FIND CLOSEST NODE TO EACH HEX CENTROID FOR EACH LTS *IF* NODE IS WITHIN HEXAGON
    -- MAKE node_lts_access columns
    -- JOIN TO Hexagons
    -- find the one closest to the centroid? 
    -- VIEWS?
    -- - FOR each LTS / component TABLE: 
    -- -    FOR each intersecting component WITH A hexagon,
    --          find node closest TO centroid - Store nodes - FOR each node,
    --          compute pgr driving distance USING THE edge components FOR that levels - Store TO each hex (total VALUE)