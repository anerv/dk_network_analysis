--- *********** ---
ALTER TABLE
    reach.lts_1_reach
ADD
    COLUMN IF NOT EXISTS edges_reached VARCHAR DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS edge_length NUMERIC DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS convex_hull GEOMETRY,
ADD
    COLUMN IF NOT EXISTS coverage_area NUMERIC DEFAULT NULL;

WITH joined_edges AS (
    SELECT
        start_node,
        array_agg(e.id) AS reachable_edges,
        SUM(ST_Length(e.geometry)) AS total_length -- OBS: Not using bike or car length
    FROM
        reach.lts_1_reach
        JOIN lts_1_edges e ON e.source = ANY(reach.lts_1_reach.reachable_nodes)
        AND e.target = ANY(reach.lts_1_reach.reachable_nodes)
    GROUP BY
        start_node
)
UPDATE
    reach.lts_1_reach
SET
    edges_reached = j.reachable_edges,
    edge_length = j.total_length
FROM
    joined_edges j
WHERE
    reach.lts_1_reach.start_node = j.start_node;

WITH joined_nodes AS (
    SELECT
        start_node,
        ST_ConcaveHull(ST_Collect(n.geometry), 0.4, FALSE) AS geometry
    FROM
        reach.lts_1_reach
        JOIN nodes n ON n.id = ANY(reach.lts_1_reach.reachable_nodes)
    GROUP BY
        start_node
)
UPDATE
    reach.lts_1_reach
SET
    convex_hull = j.geometry,
    coverage_area = ST_Area(j.geometry)
FROM
    joined_nodes j
WHERE
    reach.lts_1_reach.start_node = j.start_node;