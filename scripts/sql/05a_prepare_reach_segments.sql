DROP SCHEMA IF EXISTS reach CASCADE;

CREATE SCHEMA reach;

DROP TABLE IF EXISTS reach.edge_segments;

-- ***** Create edge tables for each LTS level and car *****
-- CREATE SEGMENTS of MAX 1 km length
WITH DATA(id, geom) AS (
    SELECT
        id,
        geometry
    FROM
        edges
    WHERE
        lts_access IN (1, 2, 3, 4, 7)
)
SELECT
    ROW_NUMBER () OVER () AS id,
    id AS edge_id,
    i,
    ST_LineSubstring(geom, startfrac, LEAST(endfrac, 1)) AS geom INTO reach.edge_segments
FROM
    (
        SELECT
            id,
            geom,
            ST_Length(geom) len,
            9999 sublen
        FROM
            DATA
    ) AS d
    CROSS JOIN LATERAL (
        SELECT
            i,
            (sublen * i) / len AS startfrac,
            (sublen * (i + 1)) / len AS endfrac
        FROM
            generate_series(0, floor(len / sublen) :: INTEGER) AS t(i)
        WHERE
            (sublen * i) / len <> 1.0
    ) AS d2;

ALTER TABLE
    reach.edge_segments DROP COLUMN IF EXISTS id,
    DROP COLUMN IF EXISTS i;

ALTER TABLE
    reach.edge_segments
ADD
    COLUMN IF NOT EXISTS id_int SERIAL,
ADD
    COLUMN IF NOT EXISTS id BIGINT;

UPDATE
    reach.edge_segments
SET
    id = id_int;

CREATE INDEX edge_segments_id ON reach.edge_segments (edge_id);

ALTER TABLE
    reach.edge_segments
ADD
    COLUMN IF NOT EXISTS lts_access INT,
ADD
    COLUMN IF NOT EXISTS lts_1_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_2_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_3_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS lts_4_gap BOOLEAN,
ADD
    COLUMN IF NOT EXISTS car_traffic BOOLEAN;

UPDATE
    reach.edge_segments
SET
    lts_access = e.lts_access,
    lts_1_gap = e.lts_1_gap,
    lts_2_gap = e.lts_2_gap,
    lts_3_gap = e.lts_3_gap,
    lts_4_gap = e.lts_4_gap,
    car_traffic = e.car_traffic
FROM
    edges e
WHERE
    e.id = edge_id;

-- REDO TOPOLOGY FOR THE SEGMENTS
ALTER TABLE
    reach.edge_segments
ADD
    COLUMN IF NOT EXISTS source BIGINT,
ADD
    COLUMN IF NOT EXISTS target BIGINT,
ADD
    COLUMN IF NOT EXISTS km FLOAT;

ALTER TABLE
    reach.edge_segments RENAME COLUMN geom TO geometry;

UPDATE
    reach.edge_segments
SET
    km = ST_Length(geometry) / 1000;

ALTER TABLE
    reach.edge_segments
ADD
    COLUMN component_size_1 DECIMAL,
ADD
    COLUMN component_size_1_2 DECIMAL,
ADD
    COLUMN component_size_1_3 DECIMAL,
ADD
    COLUMN component_size_1_4 DECIMAL,
ADD
    COLUMN component_size_car DECIMAL;

CREATE INDEX IF NOT EXISTS comp_edges_id ON fragmentation.component_edges (id);

UPDATE
    reach.edge_segments
SET
    component_size_1 = ce.component_size_1
FROM
    fragmentation.component_edges ce
WHERE
    ce.id = edge_id;

UPDATE
    reach.edge_segments
SET
    component_size_1_2 = ce.component_size_1_2
FROM
    fragmentation.component_edges ce
WHERE
    ce.id = edge_id;

UPDATE
    reach.edge_segments
SET
    component_size_1_3 = ce.component_size_1_3
FROM
    fragmentation.component_edges ce
WHERE
    ce.id = edge_id;

UPDATE
    reach.edge_segments
SET
    component_size_1_4 = ce.component_size_1_4
FROM
    fragmentation.component_edges ce
WHERE
    ce.id = edge_id;

UPDATE
    reach.edge_segments
SET
    component_size_car = ce.component_size_car
FROM
    fragmentation.component_edges ce
WHERE
    ce.id = edge_id;