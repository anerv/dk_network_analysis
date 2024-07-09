DROP TABLE IF EXISTS clustering.socio_cluster_results;

DROP SCHEMA IF EXISTS clustering CASCADE;

CREATE SCHEMA clustering;

CREATE TABLE clustering.socio_cluster_results AS
SELECT
    sc.network_rank,
    sc.socio_label,
    socio. *
FROM
    socio_clusters sc
    INNER JOIN socio ON sc.id = socio.id;

DROP TABLE IF EXISTS socio_clusters;