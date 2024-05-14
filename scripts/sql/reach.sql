DROP TABLE IF EXISTS lts_1_edges;

DROP TABLE IF EXISTS lts_2_edges;

DROP TABLE IF EXISTS lts_3_edges;

DROP TABLE IF EXISTS lts_4_edges;

DROP TABLE IF EXISTS car_edges;

DROP TABLE IF EXISTS lts_1_reach;

DROP TABLE IF EXISTS lts_2_reach;

DROP TABLE IF EXISTS lts_3_reach;

DROP TABLE IF EXISTS lts_4_reach;

DROP TABLE IF EXISTS car_reach;

CREATE TABLE lts_1_edges AS
SELECT
    id,
    km,
    source,
    target,
    geometry
FROM
    edges
WHERE
    lts_access IN (1)
    OR lts_1_gap IS TRUE;

CREATE TABLE lts_2_edges AS
SELECT
    id,
    km,
    source,
    target,
    geometry
FROM
    edges
WHERE
    lts_access IN (1, 2)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE;

CREATE TABLE lts_3_edges AS
SELECT
    id,
    km,
    source,
    target,
    geometry
FROM
    edges
WHERE
    lts_access IN (1, 2, 3)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE
    OR lts_3_gap IS TRUE;

CREATE TABLE lts_4_edges AS
SELECT
    id,
    km,
    source,
    target,
    geometry
FROM
    edges
WHERE
    lts_access IN (1, 2, 3, 4)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE
    OR lts_3_gap IS TRUE
    OR lts_4_gap IS TRUE;

CREATE TABLE car_edges AS
SELECT
    id,
    km,
    source,
    target,
    geometry
FROM
    edges
WHERE
    lts_access IN (1, 2, 3, 4, 7)
    AND car_traffic IS TRUE;

CREATE INDEX lts1_source ON lts_1_edges (source);

CREATE INDEX lts1_target ON lts_1_edges (target);

CREATE INDEX lts2_source ON lts_2_edges (source);

CREATE INDEX lts2_target ON lts_2_edges (target);

CREATE INDEX lts3_source ON lts_3_edges (source);

CREATE INDEX lts3_target ON lts_3_edges (target);

CREATE INDEX lts4_source ON lts_4_edges (source);

CREATE INDEX lts4_target ON lts_4_edges (target);

CREATE INDEX car_source ON car_edges (source);

CREATE INDEX car_target ON car_edges (target);

--- *********** ---
-- COMPUTING REACHABLE NODES FROM EACH HEXAGON
---- *********** ---
CREATE TABLE lts_1_reach AS WITH start_points AS (
    SELECT
        node_id
    FROM
        reach_lts_1
)
SELECT
    from_v AS start_node,
    ARRAY_AGG(
        node
        ORDER BY
            node
    ) AS reachable_nodes,
    ARRAY_AGG(
        edge
        ORDER BY
            edge
    ) AS reachable_edges
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM lts_1_edges',
        (
            SELECT
                ARRAY(
                    SELECT
                        node_id
                    FROM
                        start_points
                )
        ),
        5,
        -- MAX DISTANCE IN KM
        FALSE
    )
GROUP BY
    from_v;

CREATE TABLE lts_2_reach AS WITH start_points AS (
    SELECT
        node_id
    FROM
        reach_lts_2
)
SELECT
    from_v AS start_node,
    ARRAY_AGG(
        node
        ORDER BY
            node
    ) AS reachable_nodes
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM lts_2_edges',
        (
            SELECT
                ARRAY(
                    SELECT
                        node_id
                    FROM
                        start_points
                )
        ),
        5,
        -- MAX DISTANCE IN KM
        FALSE
    )
GROUP BY
    from_v;

CREATE TABLE lts_3_reach AS WITH start_points AS (
    SELECT
        node_id
    FROM
        reach_lts_3
)
SELECT
    from_v AS start_node,
    ARRAY_AGG(
        node
        ORDER BY
            node
    ) AS reachable_nodes
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM lts_3_edges',
        (
            SELECT
                ARRAY(
                    SELECT
                        node_id
                    FROM
                        start_points
                )
        ),
        5,
        -- MAX DISTANCE IN KM
        FALSE
    )
GROUP BY
    from_v;

CREATE TABLE lts_4_reach AS WITH start_points AS (
    SELECT
        node_id
    FROM
        reach_lts_4
)
SELECT
    from_v AS start_node,
    ARRAY_AGG(
        node
        ORDER BY
            node
    ) AS reachable_nodes
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM lts_4_edges',
        (
            SELECT
                ARRAY(
                    SELECT
                        node_id
                    FROM
                        start_points
                )
        ),
        5,
        -- MAX DISTANCE IN KM
        FALSE
    )
GROUP BY
    from_v;

CREATE TABLE car_reach AS WITH start_points AS (
    SELECT
        node_id
    FROM
        reach_lts_car
)
SELECT
    from_v AS start_node,
    ARRAY_AGG(
        node
        ORDER BY
            node
    ) AS reachable_nodes
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM car_edges',
        (
            SELECT
                ARRAY(
                    SELECT
                        node_id
                    FROM
                        start_points
                )
        ),
        5,
        -- MAX DISTANCE IN KM
        FALSE
    )
GROUP BY
    from_v;

--- *********** ---
-- FOR EACH HEX AND EACH LTS - GET REACHABLE EDGES
-- GET LENGTH OF REACHABLE EDGES
-- CONSTRUCT COVERAGE -- STORE POLY AND STORE AREA
ALTER TABLE
    lts_1_reach
ADD
    COLUMN edges_reached VARCHAR DEFAULT NULL,
ADD
    COLUMN edge_length NUMERIC DEFAULT NULL,
ADD
    COLUMN convex_hull GEOMETRY,
ADD
    COLUMN coverage_area NUMERIC DEFAULT NULL;

WITH joined_edges AS (
    SELECT
        start_node,
        array_agg(e.id) AS reachable_edges,
        SUM(ST_Length(e.geometry)) AS total_length
    FROM
        lts_1_reach
        JOIN lts_1_edges e ON e.source = ANY(lts_1_reach.reachable_nodes)
        AND e.target = ANY(lts_1_reach.reachable_nodes)
    GROUP BY
        start_node
)
UPDATE
    lts_1_reach
SET
    edges_reached = j.reachable_edges,
    edge_length = j.total_length
FROM
    joined_edges j
WHERE
    lts_1_reach.start_node = j.start_node;

WITH joined_nodes AS (
    SELECT
        start_node,
        --array_agg(node) AS reach,
        ST_ConcaveHull(ST_Collect(n.geometry), 0.4, FALSE) AS geometry
    FROM
        lts_1_reach
        JOIN nodes n ON n.id = ANY(lts_1_reach.reachable_nodes)
    GROUP BY
        start_node
)
UPDATE
    lts_1_reach
SET
    convex_hull = j.geometry,
    coverage_area = ST_Area(j.geometry)
FROM
    joined_nodes j
WHERE
    lts_1_reach.start_node = j.start_node;

-- SELECT
--     ST_ConcaveHull(ST_Collect(the_geom), 0.99, FALSE) AS geom
-- FROM
--     temp_points;
--- *********** ---
SELECT
    *
FROM
    lts_1_reach
    JOIN lts_1_edges ON lts_1_edges.source = ANY(lts_1_reach.reachable_nodes)
    AND lts_1_edges.target = ANY(lts_1_reach.reachable_nodes);

UPDATE
    lts_1_reach
SET
    edges_reached = (
        SELECT
            ARRAY_AGG(id)
        FROM
            lts_1_edges
        WHERE
            source IN ()
            AND target IN ()
    );

(
    1382310,
    1282019,
    1282020,
    1282021,
    1282024,
    1685640,
    1440755,
    1719814,
    2277227,
    1440754,
    1282018,
    2249299,
    1382308,
    924083,
    1382312,
    2078197,
    1440756,
    543418,
    1282017,
    1382309
) -------- *********** ----------
-- ALTER TABLE
--     edges
-- ADD
--     COLUMN edge_length NUMERIC DEFAULT NULL;
-- UPDATE
--     edges
-- SET
--     edge_length = ST_Length(geometry);
SELECT
    seq,
    DEPTH,
    start_vid,
    pred,
    node,
    edge,
    cost,
    agg_cost
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM edges',
        1532201,
        2,
        FALSE
    );

CREATE TABLE ISO_500 AS
SELECT
    seq,
    cost,
    node,
    edge,
    l.geom
FROM
    pgr_drivingDistance(
        'SELECT gid as id, start_id as source, end_id as target, len_km as 
         cost FROM network',
        41217,
        0.5,
        FALSE
    ) AS foo
    LEFT JOIN node l ON l.id = foo.node;

CREATE TABLE test2 AS WITH reach AS (
    SELECT
        *
    FROM
        pgr_drivingDistance(
            'SELECT id, source, target, km AS cost FROM edges WHERE lts_access IN (1)',
            313226,
            2,
            FALSE
        )
)
SELECT
    *
FROM
    nodes
WHERE
    id IN (
        SELECT
            node
        FROM
            reach
    );

----
-- FOR EACH row in a reach table:
-- run function below using the node id and associated edges
-- store result as edges reached (ids) -- to be used for coverage
-- maybe also sum of agg costs (represents edge lengts)
CREATE TABLE tezt AS WITH start_points AS (
    SELECT
        node_id
    FROM
        reach_lts_1
)
SELECT
    from_v AS start_node,
    ARRAY_AGG(node) AS reachable_nodes
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM lts_1_edges',
        (
            SELECT
                ARRAY(
                    SELECT
                        node_id
                    FROM
                        start_points
                )
        ),
        2,
        FALSE
    )
WHERE
    edge <> -1
GROUP BY
    from_v;

CREATE TABLE joined_tezt_node AS
SELECT
    *
FROM
    tezt_node t
    JOIN reach_lts_1 ON node_id = t.start_node;

-- THEN: GROUP BY from_v, aggregate edges
-- THEN - check issue with cut-off - find some with agg_cost much less than 2km - is this because of the cut-off?
----
SELECT
    *
FROM
    pgr_drivingDistance(
        'SELECT id, source, target, km AS cost FROM edges WHERE lts_access IN (1)',
        313226,
        2,
        FALSE
    );

SELECT
    start_point.node_id AS start_point_id,
    reachable_network.edge AS reachable_edge_id
FROM
    reach_lts_1 AS start_point
    CROSS JOIN LATERAL (
        SELECT
            edge,
            agg_cost
        FROM
            pgr_drivingDistance(
                'SELECT id, source, target, km AS cost FROM lts_1_edges',
                start_point.node_id,
                2,
                FALSE
            )
    ) AS reachable_network;

CREATE TEMP TABLE temp_driving_distances AS
SELECT
    start_point.id AS start_point_id,
    reachable_node.node AS reachable_node_id,
    reachable_node.cost AS driving_distance
FROM
    starting_points AS start_point
    CROSS JOIN LATERAL (
        SELECT
            seq,
            node,
            cost
        FROM
            pgr_drivingDistance(
                'SELECT id, source, target, cost FROM your_edge_table',
                -- Replace 'your_edge_table' with the name of your edge table
                start_point.id,
                -- Start node ID
                2000,
                -- Distance in meters (2 km = 2000 meters)
                FALSE,
                -- Directed graph (false for undirected)
                FALSE -- Restrict graph traversal by cost (false to include all nodes within distance)
            )
    ) AS reachable_node;

-- Select distinct reachable nodes within 2 km for each starting point
SELECT
    DISTINCT ON (start_point_id) start_point_id,
    reachable_node_id,
    driving_distance
FROM
    temp_driving_distances;

---
CREATE TEMP TABLE temp_driving_distances AS
SELECT
    start_points.id AS start_point_id,
    reachable_node.node AS reachable_node_id,
    reachable_node.cost AS driving_distance
FROM
    (
        SELECT
            node_id
        FROM
            lts_1_test -- Replace with the name of your starting points table
            -- WHERE
            --     condition = 'your_condition' -- Add any condition to filter starting points if needed
    ) AS start_points
    CROSS JOIN LATERAL (
        SELECT
            seq,
            node,
            cost
        FROM
            pgr_drivingDistance(
                'SELECT id, source, target, km AS cost FROM lts_1_edges',
                start_points.node_id,
                2,
                FALSE,
            )
    ) AS reachable_node;

-- Select distinct reachable nodes within 2 km for each starting point
SELECT
    DISTINCT ON (start_point_id) start_point_id,
    reachable_node_id,
    driving_distance
FROM
    temp_driving_distances;