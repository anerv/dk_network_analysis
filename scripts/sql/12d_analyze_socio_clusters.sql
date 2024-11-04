DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_clusters;

DROP TABLE IF EXISTS clustering.grouped_intersection;

CREATE INDEX IF NOT EXISTS socio_cluster_geom_ix ON clustering.socio_socio_clusters USING GIST (geometry);

CREATE TABLE clustering.dissolved_hex_clusters AS WITH union_geoms AS (
    SELECT
        ST_Union(geometry) AS geometry,
        kmeans_net_5 AS bikeability_cluster
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
    area_hex_cluster_1 = ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 1;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_2 = ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 2;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_3 = ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 3;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_4 = ST_Area(sc.geometry)
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = sc.id
    AND cg.bikeability_cluster = 4;

UPDATE
    clustering.socio_socio_clusters sc
SET
    area_hex_cluster_5 = ST_Area(sc.geometry)
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

DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_clusters;

DROP TABLE IF EXISTS clustering.grouped_intersection;