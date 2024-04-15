DROP TABLE IF EXISTS component_edges;

DROP TABLE IF EXISTS component_size;

CREATE TABLE component_edges AS
SELECT
    id,
    highway,
    --bike_length,
    component_all,
    component_1,
    component_1_2,
    component_1_3,
    component_1_4,
    component_car,
    geometry
FROM
    edges
WHERE
    component_all IS NOT NULL;

CREATE TABLE component_size AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS LENGTH,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        component_edges
    WHERE
        component_all IS NOT NULL
    GROUP BY
        component_all
);

DELETE FROM
    component_edges
WHERE
    component_all IN (
        SELECT
            component_all
        FROM
            component_size
        WHERE
            LENGTH < 100
            AND 'cycleway' <> ANY (highways)
    );