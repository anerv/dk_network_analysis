CREATE TABLE clustering.socio_cluster_results AS
SELECT
    sn.network_rank,
    ss.socio_label,
    socio. *
FROM
    clustering.socio_network_clusters sn
    INNER JOIN socio ON sn.id = socio.id
    INNER JOIN clustering.socio_socio_clusters ss ON sn.id = ss.id;