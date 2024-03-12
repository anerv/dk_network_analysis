-- NEEDS COMPONENT INFO
ALTER TABLE
    edges
ADD
    COLUMN IF NOT EXISTS lts_1_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_2_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_3_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_4_gap BOOLEAN;

CREATE VIEW nodes_lts_1 AS WITH nodes AS (
    SELECT
        source AS node
    FROM
        edges
    WHERE
        lts = 1
    UNION
    SELECT
        target AS node
    FROM
        edges
    WHERE
        lts = 1
)
SELECT
    DISTINCT node
FROM
    nodes;

CREATE VIEW nodes_lts_2 AS WITH nodes AS (
    SELECT
        source AS node
    FROM
        edges
    WHERE
        lts = 2
    UNION
    SELECT
        target AS node
    FROM
        edges
    WHERE
        lts = 2
)
SELECT
    DISTINCT node
FROM
    nodes;

CREATE VIEW nodes_lts_3 AS WITH nodes AS (
    SELECT
        source AS node
    FROM
        edges
    WHERE
        lts = 3
    UNION
    SELECT
        target AS node
    FROM
        edges
    WHERE
        lts = 3
)
SELECT
    DISTINCT node
FROM
    nodes;

CREATE VIEW nodes_lts_4 AS WITH nodes AS (
    SELECT
        source AS node
    FROM
        edges
    WHERE
        lts = 4
    UNION
    SELECT
        target AS node
    FROM
        edges
    WHERE
        lts = 4
)
SELECT
    DISTINCT node
FROM
    nodes;

-- for each node view:
-- select all edges where both start and end node is in view
-- mark them as that gap
-- TODO: SEE HOW MANY GAPS HAVE CYCLING NOT ALLOWED OR NO ACCESS
WITH node_sel AS (
    SELECT
        node
    FROM
        nodes_lts_1
    ORDER BY
        node
),
lts_1_gaps AS (
    SELECT
        *
    FROM
        edges
    WHERE
        lts <> 1
        AND km <= 30
        AND all_access = TRUE -- AND cycling_allowed = TRUE
        AND source IN (
            SELECT
                *
            FROM
                node_sel
        )
        AND target IN (
            SELECT
                *
            FROM
                node_sel
        )
)
UPDATE
    edges
SET
    lts_1_gap = TRUE
WHERE
    id IN (
        SELECT
            id
        FROM
            lts_1_gaps
    );

----
WITH lts_1_gaps AS (
    SELECT
        *
    FROM
        edges
    WHERE
        source IN (
            SELECT
                node
            FROM
                nodes_lts_1
        )
        AND target IN (
            SELECT
                node
            FROM
                nodes_lts_1
        )
        AND lts <> 1
        AND km <= 30
        AND all_access = TRUE -- AND cycling_allowed = TRUE
)
UPDATE
    edges
SET
    lts_1_gap = TRUE
WHERE
    id IN (
        SELECT
            id
        FROM
            lts_1_gaps
    );