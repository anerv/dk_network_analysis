DROP TABLE IF EXISTS fragmentation.component_length_muni;

DROP TABLE IF EXISTS fragmentation.component_length_socio;

DROP TABLE IF EXISTS fragmentation.component_length_hex;

CREATE TABLE fragmentation.component_length_muni AS (
    SELECT
        dens.municipality,
        dens.lts_1_length,
        dens.lts_2_length,
        dens.lts_3_length,
        dens.lts_4_length,
        dens.lts_1_2_length,
        dens.lts_1_3_length,
        dens.lts_1_4_length,
        dens.total_car_length,
        dens.total_network_length,
        dens.lts_1_dens,
        dens.lts_1_2_dens,
        dens.lts_1_3_dens,
        dens.lts_1_4_dens,
        dens.total_car_dens,
        dens.total_network_dens,
        dens.geometry,
        comp.component_all_count,
        comp.component_1_count,
        comp.component_1_2_count,
        comp.component_1_3_count,
        comp.component_1_4_count,
        comp.component_car_count
    FROM
        density.density_municipality dens
        JOIN fragmentation.component_count_muni comp USING (municipality)
);

CREATE TABLE fragmentation.component_length_socio AS (
    SELECT
        dens.id,
        dens.lts_1_length,
        dens.lts_2_length,
        dens.lts_3_length,
        dens.lts_4_length,
        dens.lts_1_2_length,
        dens.lts_1_3_length,
        dens.lts_1_4_length,
        dens.total_car_length,
        dens.total_network_length,
        dens.lts_1_dens,
        dens.lts_1_2_dens,
        dens.lts_1_3_dens,
        dens.lts_1_4_dens,
        dens.total_car_dens,
        dens.total_network_dens,
        dens.geometry,
        comp.component_all_count,
        comp.component_1_count,
        comp.component_1_2_count,
        comp.component_1_3_count,
        comp.component_1_4_count,
        comp.component_car_count
    FROM
        density.density_socio dens
        JOIN fragmentation.component_count_socio comp ON dens.id = comp.id
);

CREATE TABLE fragmentation.component_length_hex AS (
    SELECT
        dens.hex_id,
        dens.lts_1_length,
        dens.lts_2_length,
        dens.lts_3_length,
        dens.lts_4_length,
        dens.lts_1_2_length,
        dens.lts_1_3_length,
        dens.lts_1_4_length,
        dens.total_car_length,
        dens.total_network_length,
        dens.lts_1_dens,
        dens.lts_1_2_dens,
        dens.lts_1_3_dens,
        dens.lts_1_4_dens,
        dens.total_car_dens,
        dens.total_network_dens,
        dens.geometry,
        comp.component_all_count,
        comp.component_1_count,
        comp.component_1_2_count,
        comp.component_1_3_count,
        comp.component_1_4_count,
        comp.component_car_count
    FROM
        density.density_hex dens
        JOIN fragmentation.component_count_hex comp ON dens.hex_id = comp.hex_id
);

ALTER TABLE
    fragmentation.component_length_muni
ADD
    COLUMN component_per_length_all DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_2 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_3 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_4 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_car DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_length_socio
ADD
    COLUMN component_per_length_all DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_2 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_3 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_4 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_car DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_length_hex
ADD
    COLUMN component_per_length_all DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_2 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_3 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_1_4 DOUBLE PRECISION,
ADD
    COLUMN component_per_length_car DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_length_muni
ADD
    COLUMN component_per_dens_all DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_2 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_3 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_4 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_car DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_length_socio
ADD
    COLUMN component_per_dens_all DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_2 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_3 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_4 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_car DOUBLE PRECISION;

ALTER TABLE
    fragmentation.component_length_hex
ADD
    COLUMN component_per_dens_all DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_2 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_3 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_1_4 DOUBLE PRECISION,
ADD
    COLUMN component_per_dens_car DOUBLE PRECISION;

UPDATE
    fragmentation.component_length_muni
SET
    component_per_length_all = component_all_count / total_network_length,
    component_per_length_1 = component_1_count / lts_1_length,
    component_per_length_1_2 = component_1_2_count / lts_1_2_length,
    component_per_length_1_3 = component_1_3_count / lts_1_3_length,
    component_per_length_1_4 = component_1_4_count / lts_1_4_length,
    component_per_length_car = component_car_count / total_car_length;

UPDATE
    fragmentation.component_length_muni
SET
    component_per_dens_all = component_all_count / total_network_dens,
    component_per_dens_1 = component_1_count / lts_1_dens,
    component_per_dens_1_2 = component_1_2_count / lts_1_2_dens,
    component_per_dens_1_3 = component_1_3_count / lts_1_3_dens,
    component_per_dens_1_4 = component_1_4_count / lts_1_4_dens,
    component_per_dens_car = component_car_count / total_car_dens;

UPDATE
    fragmentation.component_length_socio
SET
    component_per_length_all = component_all_count / total_network_length,
    component_per_length_1 = component_1_count / lts_1_length,
    component_per_length_1_2 = component_1_2_count / lts_1_2_length,
    component_per_length_1_3 = component_1_3_count / lts_1_3_length,
    component_per_length_1_4 = component_1_4_count / lts_1_4_length,
    component_per_length_car = component_car_count / total_car_length;

UPDATE
    fragmentation.component_length_socio
SET
    component_per_dens_all = component_all_count / total_network_dens,
    component_per_dens_1 = component_1_count / lts_1_dens,
    component_per_dens_1_2 = component_1_2_count / lts_1_2_dens,
    component_per_dens_1_3 = component_1_3_count / lts_1_3_dens,
    component_per_dens_1_4 = component_1_4_count / lts_1_4_dens,
    component_per_dens_car = component_car_count / total_car_dens;

UPDATE
    fragmentation.component_length_hex
SET
    component_per_length_all = component_all_count / total_network_length
WHERE
    (
        total_network_length > 0
        AND total_network_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_length_1 = component_1_count / lts_1_length
WHERE
    (
        lts_1_length > 0
        AND lts_1_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_length_1_2 = component_1_2_count / lts_1_2_length
WHERE
    (
        lts_1_2_length > 0
        AND lts_1_2_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_length_1_3 = component_1_3_count / lts_1_3_length
WHERE
    (
        lts_1_3_length > 0
        AND lts_1_3_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_length_1_4 = component_1_4_count / lts_1_4_length
WHERE
    (
        lts_1_4_length > 0
        AND lts_1_4_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_length_car = component_car_count / total_car_length
WHERE
    (
        total_car_length > 0
        AND total_car_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_dens_all = component_all_count / total_network_dens
WHERE
    (
        total_network_length > 0
        AND total_network_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_dens_1 = component_1_count / lts_1_dens
WHERE
    (
        lts_1_length > 0
        AND lts_1_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_dens_1_2 = component_1_2_count / lts_1_2_dens
WHERE
    (
        lts_1_2_length > 0
        AND lts_1_2_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_dens_1_3 = component_1_3_count / lts_1_3_dens
WHERE
    (
        lts_1_3_length > 0
        AND lts_1_3_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_dens_1_4 = component_1_4_count / lts_1_4_dens
WHERE
    (
        lts_1_4_length > 0
        AND lts_1_4_length IS NOT NULL
    );

UPDATE
    fragmentation.component_length_hex
SET
    component_per_dens_car = component_car_count / total_car_dens
WHERE
    (
        total_car_length > 0
        AND total_car_length IS NOT NULL
    );