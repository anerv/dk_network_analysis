CREATE TABLE comp_count_muni AS (
    SELECT
        COUNT(DISTINCT component_all) AS comp_all_count,
        COUNT(DISTINCT component_1) AS comp_1_count,
        COUNT(DISTINCT component_1_2) AS comp_2_count,
        COUNT(DISTINCT component_1_3) AS comp_3_count,
        COUNT(DISTINCT component_1_4) AS comp_4_count,
        COUNT(DISTINCT component_car) AS comp_car_count
    FROM
        component_edges
    GROUP BY
        municipality
);

-- JOIN SPLIT EDGES TO COMPONENT EDGES
CREATE TABLE socio_component_edges AS
SELECT
    s.id,
    s.bike_length,
    s.socio_id,
    co.component_all,
    co.component_1,
    co.component_1_2,
    co.component_1_3,
    co.component_1_4,
    co.component_car
FROM
    socio_edges s
    JOIN component_edges co ON s.id = co.id;

CREATE TABLE h3_component_edges AS
SELECT
    h.id,
    h.bike_length,
    h.h3_id,
    co.component_all,
    co.component_1,
    co.component_1_2,
    co.component_1_3,
    co.component_1_4,
    co.component_car
FROM
    h3_edges h
    JOIN component_edges co ON h.id = co.id;

CREATE TABLE comp_count_socio AS (
    SELECT
        COUNT(DISTINCT component_all) AS comp_all_count,
        COUNT(DISTINCT component_1) AS comp_1_count,
        COUNT(DISTINCT component_1_2) AS comp_2_count,
        COUNT(DISTINCT component_1_3) AS comp_3_count,
        COUNT(DISTINCT component_1_4) AS comp_4_count,
        COUNT(DISTINCT component_car) AS comp_car_count
    FROM
        socio_component_edges
    GROUP BY
        socio_id
);

CREATE TABLE comp_count_h3 AS (
    SELECT
        COUNT(DISTINCT component_all) AS comp_all_count,
        COUNT(DISTINCT component_1) AS comp_1_count,
        COUNT(DISTINCT component_1_2) AS comp_2_count,
        COUNT(DISTINCT component_1_3) AS comp_3_count,
        COUNT(DISTINCT component_1_4) AS comp_4_count,
        COUNT(DISTINCT component_car) AS comp_car_count
    FROM
        h3_component_edges
    GROUP BY
        h3_id
);