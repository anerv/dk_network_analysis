-- TODO: use hex centroids for overlaps? Look at how it is done in 12d
CREATE TABLE hex_socio_intersection AS
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
    low_res_areas AS socio_socio_clusters
    JOIN high_res_areas AS hex_clusters ON ST_Intersects(socio_socio_clusters.geom, hex_clusters.geom);

CREATE TEMP TABLE low_res_areas_total AS
SELECT
    id AS low_res_id,
    ST_Area(geom) AS total_area
FROM
    low_res_areas;

CREATE TABLE weighted_scores AS
SELECT
    o.low_res_id,
    o.high_res_id,
    o.score,
    (o.score * (o.overlap_area / t.total_area)) AS weighted_score
FROM
    OVERLAPS o
    JOIN low_res_areas_total t ON o.low_res_id = t.low_res_id;

SELECT
    low_res_id,
    SUM(weighted_score) AS average_score
FROM
    weighted_scores
GROUP BY
    low_res_id
ORDER BY
    low_res_id;