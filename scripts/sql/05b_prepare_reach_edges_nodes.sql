DROP TABLE IF EXISTS reach.lts_1_segments;

DROP TABLE IF EXISTS reach.lts_1_2_segments;

DROP TABLE IF EXISTS reach.lts_1_3_segments;

DROP TABLE IF EXISTS reach.lts_1_4_segments;

DROP TABLE IF EXISTS reach.car_segments;

DROP TABLE IF EXISTS reach.segment_nodes;

-- Rename and update table and columns
-- TODO CHECK
ALTER TABLE
    reach.edge_segments_vertices_pgr RENAME TO segment_nodes;

ALTER TABLE
    reach.segment_nodes RENAME COLUMN the_geom TO geometry;

-- ***** Create edge tables for each LTS level and car *****
CREATE TABLE reach.lts_1_segments AS
SELECT
    id,
    km,
    source,
    target,
    geometry,
    lts_access,
    lts_1_gap
FROM
    reach.edge_segments
WHERE
    lts_access IN (1)
    OR lts_1_gap IS TRUE;

CREATE TABLE reach.lts_1_2_segments AS
SELECT
    id,
    km,
    source,
    target,
    geometry,
    lts_access,
    lts_1_gap,
    lts_2_gap
FROM
    reach.edge_segments
WHERE
    lts_access IN (1, 2)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE;

CREATE TABLE reach.lts_1_3_segments AS
SELECT
    id,
    km,
    source,
    target,
    geometry,
    lts_access,
    lts_1_gap,
    lts_2_gap,
    lts_3_gap
FROM
    reach.edge_segments
WHERE
    lts_access IN (1, 2, 3)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE
    OR lts_3_gap IS TRUE;

CREATE TABLE reach.lts_1_4_segments AS
SELECT
    id,
    km,
    source,
    target,
    geometry,
    lts_access,
    lts_1_gap,
    lts_2_gap,
    lts_3_gap,
    lts_4_gap
FROM
    reach.edge_segments
WHERE
    lts_access IN (1, 2, 3, 4)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE
    OR lts_3_gap IS TRUE
    OR lts_4_gap IS TRUE;

CREATE TABLE reach.car_segments AS
SELECT
    id,
    km,
    source,
    target,
    geometry,
    lts_access
FROM
    reach.edge_segments
WHERE
    lts_access IN (1, 2, 3, 4, 7)
    AND car_traffic IS TRUE;

-- index by source and target - needed for later computations
CREATE INDEX lts1_source ON reach.lts_1_segments (source);

CREATE INDEX lts1_target ON reach.lts_1_segments (target);

CREATE INDEX lts2_source ON reach.lts_1_2_segments (source);

CREATE INDEX lts2_target ON reach.lts_1_2_segments (target);

CREATE INDEX lts3_source ON reach.lts_1_3_segments (source);

CREATE INDEX lts3_target ON reach.lts_1_3_segments (target);

CREATE INDEX lts4_source ON reach.lts_1_4_segments (source);

CREATE INDEX lts4_target ON reach.lts_1_4_segments (target);

CREATE INDEX car_source ON reach.car_segments (source);

CREATE INDEX car_target ON reach.car_segments (target);