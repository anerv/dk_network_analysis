DROP TABLE IF EXISTS component_size_all;

CREATE TABLE component_size_all AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        edges
    WHERE
        component_all IS NOT NULL
    GROUP BY
        component_all
);

DELETE FROM
    edges
WHERE
    component_all IN (
        SELECT
            component_all
        FROM
            component_size_all
        WHERE
            geom_length < 100
            AND 'cycleway' <> ANY (highways)
    );

DELETE FROM
    edges
WHERE
    component_all IN (
        SELECT
            component_all
        FROM
            component_size_all
        WHERE
            highways = ARRAY [ 'service' ]
    );

DELETE
    *
FROM
    edges
WHERE
    component_all IN (
        SELECT
            component_all
        FROM
            component_size_all
        WHERE
            highways = ARRAY [ 'track' ]
            AND geom_length < 500
    );

DELETE
    *
FROM
    edges
WHERE
    component_all IN (
        SELECT
            component_all
        FROM
            component_size_all
        WHERE
            highways = ARRAY [ 'footway' ]
            AND geom_length < 500
    );

DROP TABLE IF EXISTS component_size_all,
components,
components_1,
components_2,
components_3,
components_4;