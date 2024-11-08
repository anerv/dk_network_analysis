DROP TABLE IF EXISTS clustering.hex_clusters;

DROP TABLE IF EXISTS clustering.hex_bikeability_socio;

DROP TABLE IF EXISTS clustering.unjoined_hex_clusters;

CREATE INDEX IF NOT EXISTS bikeability_cluster_geom_ix ON clustering.hex_clusters USING GIST (geometry);

CREATE TABLE clustering.hex_bikeability_socio AS WITH hex_centroids AS (
    SELECT
        hex_id,
        cluster_label,
        ST_Centroid(geometry) AS centroid_geometry
    FROM
        clustering.hex_clusters
)
SELECT
    hex_centroids. *,
    socio. *
FROM
    hex_centroids
    INNER JOIN socio ON ST_Within(hex_centroids.centroid_geometry, socio.geometry);

CREATE INDEX IF NOT EXISTS socio_bikeability_cluster_geom_ix ON clustering.hex_bikeability_socio USING GIST (geometry);

CREATE TABLE clustering.unjoined_hex_clusters AS WITH unjoined_hex_clusters AS (
    SELECT
        hex_id,
        cluster_label,
        geometry AS hex_geometry
    FROM
        clustering.hex_clusters
    WHERE
        hex_id NOT IN (
            SELECT
                hex_id
            FROM
                clustering.hex_bikeability_socio
        )
)
SELECT
    unjoined_hex_clusters. *,
    socio. *
FROM
    unjoined_hex_clusters
    INNER JOIN socio ON ST_Intersects(
        unjoined_hex_clusters.hex_geometry,
        socio.geometry
    );

INSERT INTO
    clustering.hex_bikeability_socio
SELECT
    *
FROM
    clustering.unjoined_hex_clusters;

DROP TABLE IF EXISTS clustering.unjoined_hex_clusters;