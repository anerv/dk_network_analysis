-- select socio areas with more than 50 percent worst bikeability and count number of households
WITH joined_socio_cluster AS (
    SELECT
        clustering.socio_socio_clusters. *,
        socio.id,
        socio.households_without_car
    FROM
        clustering.socio_socio_clusters
        JOIN socio ON clustering.socio_socio_clusters.id = socio.id
)
SELECT
    SUM(households_without_car) AS households_without_car
FROM
    joined_socio_cluster
WHERE
    share_hex_cluster_5 > 0.5;