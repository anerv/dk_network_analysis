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
    LEFT JOIN node l ON l.id = foo.node CREATE TABLE test2 AS WITH reach AS (
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