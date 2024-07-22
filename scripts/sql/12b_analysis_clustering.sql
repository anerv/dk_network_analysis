DROP TABLE IF EXISTS clustering.socio_cluster_results;

DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_cluster_results;

CREATE TABLE clustering.socio_cluster_results AS
SELECT
    sn.network_rank,
    ss.socio_label,
    socio. *
FROM
    clustering.socio_network_clusters sn
    INNER JOIN socio ON sn.id = socio.id
    INNER JOIN clustering.socio_socio_clusters ss ON sn.id = ss.id;

--CREATE INDEX IF NOT EXISTS hex_cluster_geom_ix ON clustering.hex_clusters USING GIST (geometry);
CREATE INDEX IF NOT EXISTS socio_cluster_geom_ix ON clustering.socio_cluster_results USING GIST (geometry);

CREATE TABLE clustering.dissolved_hex_clusters AS WITH union_geoms AS (
    SELECT
        ST_Union(geometry) AS geometry,
        kmeans_net_5
    FROM
        clustering.hex_clusters
    GROUP BY
        kmeans_net_5
)
SELECT
    (ST_Dump(geometry)) .geom AS geometry,
    kmeans_net_5
FROM
    union_geoms;

CREATE INDEX IF NOT EXISTS dissolved_hex_cluster_geom_ix ON clustering.dissolved_hex_clusters USING GIST (geometry);

CREATE TABLE clustering.clipped_socio_cluster_results AS
SELECT
    sc.id,
    dhc.kmeans_net_5,
    ST_Intersection(sc.geometry, dhc.geometry) AS clipped_geometry
FROM
    clustering.socio_cluster_results sc
    INNER JOIN clustering.dissolved_hex_clusters dhc ON ST_Intersects(sc.geometry, dhc.geometry);

CREATE TABLE grouped_intersection AS
SELECT
    id,
    kmeans_net_5,
    ST_Union(clipped_geometry) AS geometry,
    ST_area(ST_Union(clipped_geometry)) AS area
FROM
    clustering.clipped_socio_cluster_results
GROUP BY
    id,
    kmeans_net_5;

ALTER TABLE
    clustering.socio_cluster_results
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_0 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_1 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_2 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_3 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_4 FLOAT;

DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_cluster_results;

-- Step 1: Identify unique cluster types in table B
-- CREATE TABLE clustering.joined_hexes AS (
--     SELECT
--         cr.id,
--         h. *
--     FROM
--         clustering.socio_cluster_results cr
--         JOIN clustering.hex_clusters h ON ST_Intersects(ST_Centroid(h.geometry), cr.geometry)
-- );
-- CREATE TABLE clustering.joined_hexes_2 AS WITH unjoined_hexes AS (
--     SELECT
--         *
--     FROM
--         clustering.hex_clusters
--     WHERE
--         hex_id NOT IN (
--             SELECT
--                 hex_id
--             FROM
--                 clustering.joined_hexes
--         )
-- )
-- SELECT
--     cr.id,
--     h. *
-- FROM
--     clustering.socio_cluster_results cr
--     JOIN unjoined_hexes h ON ST_Intersects(h.geometry, cr.geometry);
-- INSERT INTO
--     clustering.joined_hexes (
--         id,
--         hex_id,
--         cluster_label,
--         kmeans_net_5,
--         geometry
--     )
-- SELECT
--     *
-- FROM
--     clustering.joined_hexes_2;
-- CREATE VIEW clustering.hex_cluster_counts AS
-- SELECT
--     id,
--     COUNT(*),
--     kmeans_net_5
-- FROM
--     clustering.joined_hexes
-- GROUP BY
--     id,
--     kmeans_net_5;
-- -- AUTOMATE
-- ALTER TABLE
--     clustering.socio_cluster_results
-- ADD
--     COLUMN hex_cluster_0 INTEGER,
-- ADD
--     COLUMN hex_cluster_1 INTEGER,
-- ADD
--     COLUMN hex_cluster_2 INTEGER,
-- ADD
--     COLUMN hex_cluster_3 INTEGER,
-- ADD
--     COLUMN hex_cluster_4 INTEGER;
-- UPDATE
--     clustering.socio_cluster_results
-- SET
--     hex_cluster_0 = hcc.count
-- FROM
--     clustering.hex_cluster_counts hcc
-- WHERE
--     hcc.id = clustering.socio_cluster_results.id
--     AND hcc.kmeans_net_5 = 0;
-- UPDATE
--     clustering.socio_cluster_results
-- SET
--     hex_cluster_1 = hcc.count
-- FROM
--     clustering.hex_cluster_counts hcc
-- WHERE
--     hcc.id = clustering.socio_cluster_results.id
--     AND hcc.kmeans_net_5 = 1;
-- UPDATE
--     clustering.socio_cluster_results
-- SET
--     hex_cluster_2 = hcc.count
-- FROM
--     clustering.hex_cluster_counts hcc
-- WHERE
--     hcc.id = clustering.socio_cluster_results.id
--     AND hcc.kmeans_net_5 = 2;
-- UPDATE
--     clustering.socio_cluster_results
-- SET
--     hex_cluster_3 = hcc.count
-- FROM
--     clustering.hex_cluster_counts hcc
-- WHERE
--     hcc.id = clustering.socio_cluster_results.id
--     AND hcc.kmeans_net_5 = 3;
-- UPDATE
--     clustering.socio_cluster_results
-- SET
--     hex_cluster_4 = hcc.count
-- FROM
--     clustering.hex_cluster_counts hcc
-- WHERE
--     hcc.id = clustering.socio_cluster_results.id
--     AND hcc.kmeans_net_5 = 4;
-- ALTER TABLE
--     clustering.socio_cluster_results
-- ADD
--     COLUMN hex_cluster_total INTEGER,
-- ADD
--     COLUMN share_0 FLOAT,
-- ADD
--     COLUMN share_1 FLOAT,
-- ADD
--     COLUMN share_2 FLOAT,
-- ADD
--     COLUMN share_3 FLOAT,
-- ADD
--     COLUMN share_4 FLOAT;
-- UPDATE
--     clustering.socio_cluster_results
-- SET
--     hex_cluster_total = hex_cluster_0 + hex_cluster_1 + hex_cluster_2 + hex_cluster_3 + hex_cluster_4;
-- UPDATE
--     clustering.socio_cluster_results
-- SET
--     share_0 = hex_cluster_0 :: FLOAT / hex_cluster_total,
-- SET
--     share_1 = hex_cluster_1 :: FLOAT / hex_cluster_total,
-- SET
--     share_2 = hex_cluster_2 :: FLOAT / hex_cluster_total,
-- SET
--     share_3 = hex_cluster_3 :: FLOAT / hex_cluster_total,
-- SET
--     share_4 = hex_cluster_4 :: FLOAT / hex_cluster_total;
-- DROP TABLE IF EXISTS clustering.joined_hexes;
-- DROP TABLE IF EXISTS clustering.joined_hexes_2;