CREATE TABLE clustering.socio_cluster_results AS
SELECT
    sc.network_rank,
    sc.socio_label,
    socio. *
FROM
    clustering.socio_clusters sc
    INNER JOIN socio ON sc.id = socio.id;

DROP TABLE IF EXISTS clustering.socio_clusters;