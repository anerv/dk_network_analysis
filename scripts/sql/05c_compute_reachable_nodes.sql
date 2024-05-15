--- *********** ---
-- COMPUTING REACHABLE NODES FROM EACH HEXAGON
---- *********** ---
DROP TABLE IF EXISTS lts_1_reach;

DROP TABLE IF EXISTS lts_2_reach;

DROP TABLE IF EXISTS lts_3_reach;

DROP TABLE IF EXISTS lts_4_reach;

DROP TABLE IF EXISTS car_reach;

CREATE TABLE lts_1_reach AS WITH start_points AS (
    SELECT
        node_id
    FROM
        hex_lts_1
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
        hex_lts_2
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
        hex_lts_3
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
        hex_lts_4
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
        hex_car
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