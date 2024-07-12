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

DROP TABLE IF EXISTS lts_1_gaps;

DROP TABLE IF EXISTS lts_2_gaps;

DROP TABLE IF EXISTS lts_3_gaps;

DROP TABLE IF EXISTS lts_4_gaps;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_1;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_2;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_3;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_4;

CREATE INDEX IF NOT EXISTS edges_geom_ix ON edges USING GIST (geometry);

CREATE INDEX IF NOT EXISTS lts_ix ON edges (lts);

CREATE INDEX IF NOT EXISTS source_ix ON edges (source);

CREATE INDEX IF NOT EXISTS target_ix ON edges (target);

CREATE MATERIALIZED VIEW nodes_lts_1 AS
SELECT
    DISTINCT node
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts = 1
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts = 1
    ) AS nodes;

CREATE MATERIALIZED VIEW nodes_lts_2 AS
SELECT
    DISTINCT node
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts = 2
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts = 2
    ) AS nodes;

CREATE MATERIALIZED VIEW nodes_lts_3 AS
SELECT
    DISTINCT node
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts = 3
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts = 3
    ) AS nodes;

CREATE MATERIALIZED VIEW nodes_lts_4 AS
SELECT
    DISTINCT node
FROM
    (
        SELECT
            source AS node
        FROM
            edges
        WHERE
            lts = 4
        UNION
        ALL
        SELECT
            target AS node
        FROM
            edges
        WHERE
            lts = 4
    ) AS nodes;

-- LTS GAPS 1
CREATE TABLE lts_1_gaps AS
SELECT
    e.name,
    e.municipality,
    e.id,
    e.lts,
    e.lts_access,
    e.all_access,
    e.cycling_allowed,
    e.source,
    e.target,
    e.bicycle,
    e.highway,
    e.geometry
FROM
    edges AS e
    JOIN nodes_lts_1 AS ns ON e.source = ns.node
    JOIN nodes_lts_1 AS nt ON e.target = nt.node
    LEFT JOIN components_1 AS co1 ON e.source = co1.node
    LEFT JOIN components_1 AS co2 ON e.target = co2.node
WHERE
    e.lts <> 1
    AND e.km <= 0.030
    AND e.all_access = TRUE
    AND co1.component <> co2.component;

-- LTS GAPS 2
CREATE TABLE lts_2_gaps AS
SELECT
    e.name,
    e.municipality,
    e.id,
    e.lts,
    e.lts_access,
    e.all_access,
    e.cycling_allowed,
    e.source,
    e.target,
    e.bicycle,
    e.highway,
    e.geometry
FROM
    edges AS e
    JOIN nodes_lts_2 AS ns ON e.source = ns.node
    JOIN nodes_lts_2 AS nt ON e.target = nt.node
    LEFT JOIN components_2 AS co1 ON e.source = co1.node
    LEFT JOIN components_2 AS co2 ON e.target = co2.node
WHERE
    e.lts <> 2
    AND e.km <= 0.030
    AND e.all_access = TRUE
    AND co1.component <> co2.component;

-- LTS GAPS 3
CREATE TABLE lts_3_gaps AS
SELECT
    e.name,
    e.municipality,
    e.id,
    e.lts,
    e.lts_access,
    e.all_access,
    e.cycling_allowed,
    e.source,
    e.target,
    e.bicycle,
    e.highway,
    e.geometry
FROM
    edges AS e
    JOIN nodes_lts_3 AS ns ON e.source = ns.node
    JOIN nodes_lts_3 AS nt ON e.target = nt.node
    LEFT JOIN components_3 AS co1 ON e.source = co1.node
    LEFT JOIN components_3 AS co2 ON e.target = co2.node
WHERE
    e.lts <> 3
    AND e.km <= 0.030
    AND e.all_access = TRUE
    AND co1.component <> co2.component;

-- LTS GAPS 4
CREATE TABLE lts_4_gaps AS
SELECT
    e.name,
    e.municipality,
    e.id,
    e.lts,
    e.lts_access,
    e.all_access,
    e.cycling_allowed,
    e.source,
    e.target,
    e.bicycle,
    e.highway,
    e.geometry
FROM
    edges AS e
    JOIN nodes_lts_4 AS ns ON e.source = ns.node
    JOIN nodes_lts_4 AS nt ON e.target = nt.node
    LEFT JOIN components_4 AS co1 ON e.source = co1.node
    LEFT JOIN components_4 AS co2 ON e.target = co2.node
WHERE
    e.lts <> 4
    AND e.km <= 0.030
    AND e.all_access = TRUE
    AND co1.component <> co2.component;

CREATE INDEX IF NOT EXISTS lts1_gap_geom_ix ON lts_1_gaps USING GIST (geometry);

CREATE INDEX IF NOT EXISTS lts2_gap_geom_ix ON lts_2_gaps USING GIST (geometry);

CREATE INDEX IF NOT EXISTS lts3_gap_geom_ix ON lts_3_gaps USING GIST (geometry);

CREATE INDEX IF NOT EXISTS lts4_gap_geom_ix ON lts_4_gaps USING GIST (geometry);

--DROP gaps that form too long stretches
WITH merged AS (
    SELECT
        (ST_Dump(ST_LineMerge(ST_Collect(geometry)))) .geom AS geometry
    FROM
        lts_1_gaps
),
too_long_gaps AS (
    SELECT
        --row_number() OVER () AS cid,
        l.id --,
        --m.geometry
    FROM
        merged m
        INNER JOIN lts_1_gaps l ON ST_Intersects(l.geometry, m.geometry)
    WHERE
        ST_Length(m.geometry) > 30
)
DELETE FROM
    lts_1_gaps
WHERE
    id IN (
        SELECT
            id
        FROM
            too_long_gaps
    );

WITH merged AS (
    SELECT
        (ST_Dump(ST_LineMerge(ST_Collect(geometry)))) .geom AS geometry
    FROM
        lts_2_gaps
),
too_long_gaps AS (
    SELECT
        --row_number() OVER () AS cid,
        l.id --,
        --m.geometry
    FROM
        merged m
        INNER JOIN lts_2_gaps l ON ST_Intersects(l.geometry, m.geometry)
    WHERE
        ST_Length(m.geometry) > 30
)
DELETE FROM
    lts_2_gaps
WHERE
    id IN (
        SELECT
            id
        FROM
            too_long_gaps
    );

WITH merged AS (
    SELECT
        (ST_Dump(ST_LineMerge(ST_Collect(geometry)))) .geom AS geometry
    FROM
        lts_3_gaps
),
too_long_gaps AS (
    SELECT
        --row_number() OVER () AS cid,
        l.id --,
        --m.geometry
    FROM
        merged m
        INNER JOIN lts_3_gaps l ON ST_Intersects(l.geometry, m.geometry)
    WHERE
        ST_Length(m.geometry) > 30
)
DELETE FROM
    lts_3_gaps
WHERE
    id IN (
        SELECT
            id
        FROM
            too_long_gaps
    );

WITH merged AS (
    SELECT
        (ST_Dump(ST_LineMerge(ST_Collect(geometry)))) .geom AS geometry
    FROM
        lts_4_gaps
),
too_long_gaps AS (
    SELECT
        --row_number() OVER () AS cid,
        l.id --,
        --m.geometry
    FROM
        merged m
        INNER JOIN lts_4_gaps l ON ST_Intersects(l.geometry, m.geometry)
    WHERE
        ST_Length(m.geometry) > 30
)
DELETE FROM
    lts_4_gaps
WHERE
    id IN (
        SELECT
            id
        FROM
            too_long_gaps
    );

-- CONSIDER - close gaps for pedestrian, no cycling, etc?
DELETE FROM
    lts_1_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle <> 'use_sidepath';

DELETE FROM
    lts_1_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle = 'use_sidepath'
    AND highway IN (
        'motorway',
        'motorway_link',
        'trunk',
        'trunk_link'
    );

DELETE FROM
    lts_2_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle <> 'use_sidepath';

DELETE FROM
    lts_2_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle = 'use_sidepath'
    AND highway IN (
        'motorway',
        'motorway_link',
        'trunk',
        'trunk_link'
    );

DELETE FROM
    lts_3_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle <> 'use_sidepath';

DELETE FROM
    lts_3_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle = 'use_sidepath'
    AND highway IN (
        'motorway',
        'motorway_link',
        'trunk',
        'trunk_link'
    );

DELETE FROM
    lts_4_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle <> 'use_sidepath';

DELETE FROM
    lts_4_gaps
WHERE
    lts_access IN (0, 7)
    AND bicycle = 'use_sidepath'
    AND highway IN (
        'motorway',
        'motorway_link',
        'trunk',
        'trunk_link'
    );

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

UPDATE
    edges
SET
    lts_2_gap = TRUE
WHERE
    id IN (
        SELECT
            id
        FROM
            lts_2_gaps
    );

UPDATE
    edges
SET
    lts_3_gap = TRUE
WHERE
    id IN (
        SELECT
            id
        FROM
            lts_3_gaps
    );

UPDATE
    edges
SET
    lts_4_gap = TRUE
WHERE
    id IN (
        SELECT
            id
        FROM
            lts_4_gaps
    );

DROP TABLE IF EXISTS lts_1_gaps;

DROP TABLE IF EXISTS lts_2_gaps;

DROP TABLE IF EXISTS lts_3_gaps;

DROP TABLE IF EXISTS lts_4_gaps;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_1;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_2;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_3;

DROP MATERIALIZED VIEW IF EXISTS nodes_lts_4;

DROP TABLE IF EXISTS components;

DROP TABLE IF EXISTS components_1;

DROP TABLE IF EXISTS components_2;

DROP TABLE IF EXISTS components_3;

DROP TABLE IF EXISTS components_4;