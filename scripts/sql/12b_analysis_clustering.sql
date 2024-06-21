DROP TABLE IF EXISTS socio_cluster_results;

CREATE TABLE socio_cluster_results AS
SELECT
    sc.network_rank,
    sc.socio_label,
    socio. *
FROM
    socio_clusters sc
    INNER JOIN socio ON sc.id = socio.id;

DROP TABLE IF EXISTS socio_clusters;