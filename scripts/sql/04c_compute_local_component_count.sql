DROP TABLE IF EXISTS fragmentation.comp_count_muni;

DROP TABLE IF EXISTS fragmentation.comp_count_socio;

DROP TABLE IF EXISTS fragmentation.comp_count_hex;

DROP TABLE IF EXISTS fragmentation.socio_component_edges;

DROP TABLE IF EXISTS fragmentation.hex_component_edges;

DROP TABLE IF EXISTS fragmentation.hex_largest_components;

CREATE TABLE fragmentation.comp_count_muni AS WITH comp_count AS (
    SELECT
        COUNT(DISTINCT component_all) AS comp_all_count,
        COUNT(DISTINCT component_1) AS comp_1_count,
        COUNT(DISTINCT component_1_2) AS comp_2_count,
        COUNT(DISTINCT component_1_3) AS comp_3_count,
        COUNT(DISTINCT component_1_4) AS comp_4_count,
        COUNT(DISTINCT component_car) AS comp_car_count,
        municipality
    FROM
        fragmentation.component_edges
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
CREATE TABLE fragmentation.socio_component_edges AS
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
    JOIN fragmentation.component_edges co ON s.id = co.id;

CREATE TABLE fragmentation.hex_component_edges AS
SELECT
    h.id,
    h.bike_length,
    h.hex_id,
    co.component_all,
    co.component_1,
    co.component_1_2,
    co.component_1_3,
    co.component_1_4,
    co.component_car
FROM
    hex_edges h
    JOIN fragmentation.component_edges co ON h.id = co.id;

CREATE TABLE fragmentation.comp_count_socio AS WITH comp_count AS (
    SELECT
        socio_id,
        COUNT(DISTINCT component_all) AS comp_all_count,
        COUNT(DISTINCT component_1) AS comp_1_count,
        COUNT(DISTINCT component_1_2) AS comp_2_count,
        COUNT(DISTINCT component_1_3) AS comp_3_count,
        COUNT(DISTINCT component_1_4) AS comp_4_count,
        COUNT(DISTINCT component_car) AS comp_car_count
    FROM
        fragmentation.socio_component_edges
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

CREATE TABLE fragmentation.comp_count_hex AS WITH comp_count AS (
    SELECT
        hex_id,
        COUNT(DISTINCT component_all) AS comp_all_count,
        COUNT(DISTINCT component_1) AS comp_1_count,
        COUNT(DISTINCT component_1_2) AS comp_2_count,
        COUNT(DISTINCT component_1_3) AS comp_3_count,
        COUNT(DISTINCT component_1_4) AS comp_4_count,
        COUNT(DISTINCT component_car) AS comp_car_count
    FROM
        fragmentation.hex_component_edges
    GROUP BY
        hex_id
)
SELECT
    co.hex_id,
    co.comp_all_count,
    co.comp_1_count,
    co.comp_2_count,
    co.comp_3_count,
    co.comp_4_count,
    co.comp_car_count,
    h.geometry
FROM
    comp_count co
    JOIN hex_grid h ON co.hex_id = h.hex_id;

CREATE TABLE fragmentation.hex_largest_components AS WITH joined_edges AS (
    SELECT
        h.id,
        h.hex_id,
        co1.bike_length AS component_length_1,
        co1.buffer_area AS component_coverage_1,
        co2.bike_length AS component_length_2,
        co2.buffer_area AS component_coverage_2,
        co3.bike_length AS component_length_3,
        co3.buffer_area AS component_coverage_3,
        co4.bike_length AS component_length_4,
        co4.buffer_area AS component_coverage_4,
        coc.bike_length AS component_length_car,
        coc.buffer_area AS component_coverage_car
    FROM
        fragmentation.hex_component_edges h
        LEFT JOIN fragmentation.component_size_1 co1 ON h.component_1 = co1.component_1
        LEFT JOIN fragmentation.component_size_2 co2 ON h.component_1_2 = co2.component_1_2
        LEFT JOIN fragmentation.component_size_3 co3 ON h.component_1_3 = co3.component_1_3
        LEFT JOIN fragmentation.component_size_4 co4 ON h.component_1_4 = co4.component_1_4
        LEFT JOIN fragmentation.component_size_car coc ON h.component_car = coc.component_car
)
SELECT
    hex_id,
    MAX(component_length_1) AS component_length_1,
    MAX(component_coverage_1) AS component_coverage_1,
    MAX(component_length_2) AS component_length_2,
    MAX(component_coverage_2) AS component_coverage_2,
    MAX(component_length_3) AS component_length_3,
    MAX(component_coverage_3) AS component_coverage_3,
    MAX(component_length_4) AS component_length_4,
    MAX(component_coverage_4) AS component_coverage_4,
    MAX(component_length_car) AS component_length_car,
    MAX(component_coverage_car) AS component_coverage_car
FROM
    joined_edges
GROUP BY
    hex_id;

ALTER TABLE
    fragmentation.hex_largest_components
ADD
    COLUMN geometry geometry(Polygon, 25832);

UPDATE
    fragmentation.hex_largest_components hc
SET
    geometry = h.geometry
FROM
    hex_grid h
WHERE
    hc.hex_id = h.hex_id;