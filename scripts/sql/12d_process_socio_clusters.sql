DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_clusters;

DROP TABLE IF EXISTS clustering.grouped_intersection;

DROP TABLE IF EXISTS clustering.hex_socio_intersection;

DROP TABLE IF EXISTS clustering.weighted_bikeability;

CREATE INDEX IF NOT EXISTS socio_cluster_geom_ix ON clustering.socio_socio_clusters USING GIST (geometry);

CREATE TABLE clustering.dissolved_hex_clusters AS WITH union_geoms AS (
    SELECT
        ST_Union(geometry) AS geometry,
        kmeans_net AS bikeability_cluster
    FROM
        clustering.hex_clusters
    GROUP BY
        bikeability_cluster
)
SELECT
    (ST_Dump(geometry)) .geom AS geometry,
    bikeability_cluster
FROM
    union_geoms;

CREATE INDEX IF NOT EXISTS dissolved_hex_cluster_geom_ix ON clustering.dissolved_hex_clusters USING GIST (geometry);

CREATE TABLE clustering.clipped_socio_clusters AS
SELECT
    sc.id,
    dhc.bikeability_cluster,
    ST_Intersection(sc.geometry, dhc.geometry) AS clipped_geometry
FROM
    clustering.socio_socio_clusters sc
    INNER JOIN clustering.dissolved_hex_clusters dhc ON ST_Intersects(sc.geometry, dhc.geometry);

CREATE TABLE clustering.grouped_intersection AS
SELECT
    id,
    bikeability_cluster,
    ST_Union(clipped_geometry) AS geometry,
    ST_Area(ST_Union(clipped_geometry)) AS area
FROM
    clustering.clipped_socio_clusters
GROUP BY
    id,
    bikeability_cluster;

ALTER TABLE
    clustering.socio_socio_clusters
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_1 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_2 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_3 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_4 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_5 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_1 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_2 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_3 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_4 FLOAT,
ADD
    COLUMN IF NOT EXISTS share_hex_cluster_5 FLOAT;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_1 = ST_Area(sc.geometry) / 1000000
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 1;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_2 = ST_Area(sc.geometry) / 1000000
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 2;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_3 = ST_Area(sc.geometry) / 1000000
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 3;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_4 = ST_Area(sc.geometry) / 1000000
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 4;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_5 = ST_Area(sc.geometry) / 1000000
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 5;

UPDATE
    clustering.socio_socio_clusters sc
SET
    share_hex_cluster_1 = cg.area / ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 1;

UPDATE
    clustering.socio_socio_clusters sc
SET
    share_hex_cluster_2 = cg.area / ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 2;

UPDATE
    clustering.socio_socio_clusters sc
SET
    share_hex_cluster_3 = cg.area / ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 3;

UPDATE
    clustering.socio_socio_clusters sc
SET
    share_hex_cluster_4 = cg.area / ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 4;

UPDATE
    clustering.socio_socio_clusters sc
SET
    share_hex_cluster_5 = cg.area / ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 5;

CREATE TABLE clustering.hex_socio_intersection AS
SELECT
    socio_socio_clusters.id AS socio_id,
    hex_clusters.hex_id,
    ST_Area(
        ST_Intersection(
            socio_socio_clusters.geometry,
            hex_clusters.geometry
        )
    ) AS intersect_area,
    hex_clusters.kmeans_net AS bikeability_rank
FROM
    clustering.socio_socio_clusters
    JOIN clustering.hex_clusters ON ST_Intersects(
        socio_socio_clusters.geometry,
        hex_clusters.geometry
    );

CREATE TEMP TABLE socio_areas_total AS
SELECT
    id AS socio_id,
    ST_Area(geometry) AS total_area
FROM
    clustering.socio_socio_clusters;

CREATE TEMP TABLE weighted_bikeability AS
SELECT
    inter.socio_id,
    inter.hex_id,
    inter.bikeability_rank,
    (
        inter.bikeability_rank * (inter.intersect_area / t.total_area)
    ) AS weighted_bikeability_rank
FROM
    clustering.hex_socio_intersection inter
    JOIN socio_areas_total t ON inter.socio_id = t.socio_id;

ALTER TABLE
    clustering.socio_socio_clusters
ADD
    COLUMN IF NOT EXISTS average_bikeability_rank DOUBLE PRECISION;

WITH weighted_bikeability AS (
    SELECT
        socio_id,
        SUM(weighted_bikeability_rank) AS average_bikeability_rank
    FROM
        weighted_bikeability
    GROUP BY
        socio_id
    ORDER BY
        socio_id
)
UPDATE
    clustering.socio_socio_clusters
SET
    average_bikeability_rank = wb.average_bikeability_rank
FROM
    weighted_bikeability wb
WHERE
    socio_socio_clusters.id = wb.socio_id;

DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_clusters;

DROP TABLE IF EXISTS clustering.grouped_intersection;

DROP TABLE IF EXISTS clustering.weighted_bikeability;