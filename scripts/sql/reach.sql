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