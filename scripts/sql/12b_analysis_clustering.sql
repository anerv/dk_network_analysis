DROP TABLE IF EXISTS clustering.socio_cluster_results;

DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_cluster_results;

DROP TABLE IF EXISTS clustering.grouped_intersection;

CREATE TABLE clustering.socio_cluster_results AS
SELECT
    sn.network_rank,
    ss.socio_label,
    socio. *
FROM
    clustering.socio_network_clusters sn
    INNER JOIN socio ON sn.id = socio.id
    INNER JOIN clustering.socio_socio_clusters ss ON sn.id = ss.id;

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

CREATE TABLE clustering.grouped_intersection AS
SELECT
    id,
    kmeans_net_5,
    ST_Union(clipped_geometry) AS geometry,
    ST_Area(ST_Union(clipped_geometry)) AS area
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
    COLUMN IF NOT EXISTS share_hex_cluster_4 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_0 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_1 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_2 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_3 FLOAT,
ADD
    COLUMN IF NOT EXISTS area_hex_cluster_4 FLOAT;

UPDATE
    clustering.socio_cluster_results
SET
    area_hex_cluster_0 = area
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = clustering.socio_cluster_results.id
    AND cg.kmeans_net_5 = 0;

UPDATE
    clustering.socio_cluster_results
SET
    area_hex_cluster_1 = area
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = clustering.socio_cluster_results.id
    AND cg.kmeans_net_5 = 1;

UPDATE
    clustering.socio_cluster_results
SET
    area_hex_cluster_2 = area
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = clustering.socio_cluster_results.id
    AND cg.kmeans_net_5 = 2;

UPDATE
    clustering.socio_cluster_results
SET
    area_hex_cluster_3 = area
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = clustering.socio_cluster_results.id
    AND cg.kmeans_net_5 = 3;

UPDATE
    clustering.socio_cluster_results
SET
    area_hex_cluster_4 = area
FROM
    clustering.grouped_intersection cg
WHERE
    cg.id = clustering.socio_cluster_results.id
    AND cg.kmeans_net_5 = 4;

UPDATE
    clustering.socio_cluster_results
SET
    share_hex_cluster_0 = area_hex_cluster_0 / ST_Area(geometry);

UPDATE
    clustering.socio_cluster_results
SET
    share_hex_cluster_1 = area_hex_cluster_1 / ST_Area(geometry);

UPDATE
    clustering.socio_cluster_results
SET
    share_hex_cluster_2 = area_hex_cluster_2 / ST_Area(geometry);

UPDATE
    clustering.socio_cluster_results
SET
    share_hex_cluster_3 = area_hex_cluster_3 / ST_Area(geometry);

UPDATE
    clustering.socio_cluster_results
SET
    share_hex_cluster_4 = area_hex_cluster_4 / ST_Area(geometry);

DROP TABLE IF EXISTS clustering.dissolved_hex_clusters;

DROP TABLE IF EXISTS clustering.clipped_socio_cluster_results;

DROP TABLE IF EXISTS clustering.grouped_intersection;

ALTER TABLE
    clustering.hex_clusters
ADD
    column IF NOT EXISTS population FLOAT,
ADD
    COLUMN IF NOT EXISTS population_density FLOAT,
ADD
    COLUMN IF NOT EXISTS urban_pct FLOAT;

UPDATE
    clustering.hex_clusters hc
SET
    population = hg.population,
    population_density = hg.population_density,
    urban_pct = hg.urban_pct
FROM
    hex_grid hg
WHERE
    hc.hex_id = hg.hex_id;