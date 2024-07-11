DROP SCHEMA IF EXISTS reach CASCADE;

CREATE SCHEMA reach;

DROP TABLE IF EXISTS lts_1_edges;

DROP TABLE IF EXISTS lts_1_2_edges;

DROP TABLE IF EXISTS lts_1_3_edges;

DROP TABLE IF EXISTS lts_1_4_edges;

DROP TABLE IF EXISTS car_edges;

-- ***** Create edge tables for each LTS level and car *****
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

CREATE TABLE lts_1_2_edges AS
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

CREATE TABLE lts_1_3_edges AS
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

CREATE TABLE lts_1_4_edges AS
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

-- index by source and target - needed for later computations
CREATE INDEX lts1_source ON lts_1_edges (source);

CREATE INDEX lts1_target ON lts_1_edges (target);

CREATE INDEX lts2_source ON lts_1_2_edges (source);

CREATE INDEX lts2_target ON lts_1_2_edges (target);

CREATE INDEX lts3_source ON lts_1_3_edges (source);

CREATE INDEX lts3_target ON lts_1_3_edges (target);

CREATE INDEX lts4_source ON lts_1_4_edges (source);

CREATE INDEX lts4_target ON lts_1_4_edges (target);

CREATE INDEX car_source ON car_edges (source);

CREATE INDEX car_target ON car_edges (target);