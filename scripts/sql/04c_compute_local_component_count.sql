DROP TABLE IF EXISTS comp_count_muni;

DROP TABLE IF EXISTS comp_count_socio;

DROP TABLE IF EXISTS comp_count_h3;

DROP TABLE IF EXISTS socio_component_edges;

DROP TABLE IF EXISTS h3_component_edges;

CREATE TABLE comp_count_muni AS WITH comp_count AS (
    SELECT
        COUNT(DISTINCT component_all) AS comp_all_count,
        COUNT(DISTINCT component_1) AS comp_1_count,
        COUNT(DISTINCT component_1_2) AS comp_2_count,
        COUNT(DISTINCT component_1_3) AS comp_3_count,
        COUNT(DISTINCT component_1_4) AS comp_4_count,
        COUNT(DISTINCT component_car) AS comp_car_count,
        municipality
    FROM
        component_edges
    GROUP BY
        municipality
)
SELECT
    co.municipality,
    co.comp_all_count,
    co.comp_1_count,
    co.comp_2_count,
    co.comp_3_count,
    co.comp_4_count,
    co.comp_car_count,
    mu.geometry
FROM
    comp_count co
    JOIN adm_boundaries mu ON co.municipality = mu.navn;

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

CREATE TABLE comp_count_socio AS WITH comp_count AS (
    SELECT
        socio_id,
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
)
SELECT
    co.socio_id,
    co.comp_all_count,
    co.comp_1_count,
    co.comp_2_count,
    co.comp_3_count,
    co.comp_4_count,
    co.comp_car_count,
    so.geometry
FROM
    comp_count co
    JOIN socio so ON co.socio_id = so.id;

CREATE TABLE comp_count_h3 AS WITH comp_count AS (
    SELECT
        h3_id,
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
)
SELECT
    co.h3_id,
    co.comp_all_count,
    co.comp_1_count,
    co.comp_2_count,
    co.comp_3_count,
    co.comp_4_count,
    co.comp_car_count,
    h.geometry
FROM
    comp_count co
    JOIN h3_grid h ON co.h3_id = h.hex_id;