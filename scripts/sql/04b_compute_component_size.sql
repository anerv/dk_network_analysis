DROP TABLE IF EXISTS component_edges;

DROP TABLE IF EXISTS component_size;

CREATE TABLE component_edges AS
SELECT
    id,
    highway,
    bike_length,
    municipality,
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

CREATE TABLE component_size_all AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
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
            geom_length < 100
            AND 'cycleway' <> ANY (highways)
    );

CREATE TABLE component_size_1 AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        component_edges
    WHERE
        component_1 IS NOT NULL
    GROUP BY
        component_1
);

CREATE TABLE component_size_2 AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        component_edges
    WHERE
        component_2 IS NOT NULL
    GROUP BY
        component_2
);

CREATE TABLE component_size_3 AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        component_edges
    WHERE
        component_3 IS NOT NULL
    GROUP BY
        component_3
);

CREATE TABLE component_size_4 AS (
    SELECT
        COUNT(id),
        component_all,
        SUM(ST_Length(geometry)) AS geom_length,
        SUM(bike_length) AS bike_length,
        ARRAY_AGG(DISTINCT id) AS ids,
        ARRAY_AGG(DISTINCT highway) AS highways
    FROM
        component_edges
    WHERE
        component_4 IS NOT NULL
    GROUP BY
        component_4
);