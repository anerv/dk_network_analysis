ALTER TABLE
    kbh
ADD
    COLUMN IF NOT EXISTS lts_1_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_2_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_3_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_4_gap BOOLEAN;

DROP TABLE IF EXISTS lts_1_gaps;

DROP TABLE IF EXISTS lts_2_gaps;

DROP TABLE IF EXISTS lts_3_gaps;

DROP TABLE IF EXISTS lts_4_gaps;

CREATE VIEW nodes_lts_1 AS WITH nodes AS (
    SELECT
        source AS node
    FROM
        kbh
    WHERE
        lts = 1
    UNION
    SELECT
        target AS node
    FROM
        kbh
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
        kbh
    WHERE
        lts = 2
    UNION
    SELECT
        target AS node
    FROM
        kbh
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
        kbh
    WHERE
        lts = 3
    UNION
    SELECT
        target AS node
    FROM
        kbh
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
        kbh
    WHERE
        lts = 4
    UNION
    SELECT
        target AS node
    FROM
        kbh
    WHERE
        lts = 4
)
SELECT
    DISTINCT node
FROM
    nodes;

-- LTS 1 GAPS
CREATE TABLE lts_1_gaps AS WITH node_sel AS (
    SELECT
        node
    FROM
        nodes_lts_1
    ORDER BY
        node
),
lts_1_gaps AS (
    SELECT
        id,
        lts,
        lts_access,
        all_access,
        cycling_allowed,
        km,
        source,
        target,
        geometry
    FROM
        kbh
    WHERE
        lts <> 1
        AND km <= 0.030
        AND all_access = TRUE
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
SELECT
    l.id,
    l.lts,
    l.lts_access,
    l.all_access,
    l.cycling_allowed,
    l.source,
    l.target,
    l.geometry
FROM
    lts_1_gaps l
    LEFT JOIN components_1 co1 ON l.source = co1.node
    LEFT JOIN components_1 co2 ON l.target = co2.node
WHERE
    co1.component <> co2.component;

--- LTS 2 GAPS
CREATE TABLE lts_2_gaps AS WITH node_sel AS (
    SELECT
        node
    FROM
        nodes_lts_2
    ORDER BY
        node
),
lts_2_gaps AS (
    SELECT
        id,
        lts,
        lts_access,
        all_access,
        cycling_allowed,
        km,
        source,
        target,
        geometry
    FROM
        kbh
    WHERE
        lts NOT IN (1, 2)
        AND km <= 0.030
        AND all_access = TRUE
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
SELECT
    l.id,
    l.lts,
    l.lts_access,
    l.all_access,
    l.cycling_allowed,
    l.source,
    l.target,
    l.geometry
FROM
    lts_2_gaps l
    LEFT JOIN components_2 co1 ON l.source = co1.node
    LEFT JOIN components_2 co2 ON l.target = co2.node
WHERE
    co1.component <> co2.component;

-- LTS 3 GAPS
CREATE TABLE lts_3_gaps AS WITH node_sel AS (
    SELECT
        node
    FROM
        nodes_lts_3
    ORDER BY
        node
),
lts_3_gaps AS (
    SELECT
        id,
        lts,
        lts_access,
        all_access,
        cycling_allowed,
        km,
        source,
        target,
        geometry
    FROM
        kbh
    WHERE
        lts NOT IN (1, 2, 3)
        AND km <= 0.030
        AND all_access = TRUE
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
SELECT
    l.id,
    l.lts,
    l.lts_access,
    l.all_access,
    l.cycling_allowed,
    l.source,
    l.target,
    l.geometry
FROM
    lts_3_gaps l
    LEFT JOIN components_3 co1 ON l.source = co1.node
    LEFT JOIN components_3 co2 ON l.target = co2.node
WHERE
    co1.component <> co2.component;

-- LTS 4 GAPS
CREATE TABLE lts_4_gaps AS WITH node_sel AS (
    SELECT
        node
    FROM
        nodes_lts_4
    ORDER BY
        node
),
lts_4_gaps AS (
    SELECT
        id,
        lts,
        lts_access,
        all_access,
        cycling_allowed,
        km,
        source,
        target,
        geometry
    FROM
        kbh
    WHERE
        lts NOT IN (1, 2, 3, 4)
        AND km <= 0.030
        AND all_access = TRUE
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
SELECT
    l.id,
    l.lts,
    l.lts_access,
    l.all_access,
    l.cycling_allowed,
    l.source,
    l.target,
    l.geometry
FROM
    lts_4_gaps l
    LEFT JOIN components_1 co1 ON l.source = co1.node
    LEFT JOIN components_1 co2 ON l.target = co2.node
WHERE
    co1.component <> co2.component;

-- TODO: CONSIDER NODE SELECTION FOR 2,3,4
-- GET DISTINCT COMPONENT FOR EACH gap source and target - if its the same, it is not a gap
UPDATE
    kbh
SET
    lts_1_gap = TRUE
WHERE
    id IN (
        SELECT
            id
        FROM
            lts_1_gaps
    );

DROP TABLE IF EXISTS lts_1_gaps;

DROP TABLE IF EXISTS lts_2_gaps;

DROP TABLE IF EXISTS lts_3_gaps;

DROP TABLE IF EXISTS lts_4_gaps;

DROP VIEW IF EXISTS nodes_lts_1;

DROP VIEW IF EXISTS nodes_lts_2;

DROP VIEW IF EXISTS nodes_lts_3;

DROP VIEW IF EXISTS nodes_lts_4;

```