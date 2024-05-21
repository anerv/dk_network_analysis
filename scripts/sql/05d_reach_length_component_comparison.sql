DROP TABLE IF EXISTS reach.reach_component_length_h3;

CREATE TABLE reach.reach_component_length_h3 AS (
    SELECT
        dens.hex_id,
        dens.lts_1_length,
        dens.lts_1_2_length,
        dens.lts_1_3_length,
        dens.lts_1_4_length,
        dens.total_car_length,
        dens.lts_1_dens,
        dens.lts_1_2_dens,
        dens.lts_1_3_dens,
        dens.lts_1_4_dens,
        dens.total_car_dens,
        dens.geometry,
        comp.comp_1_count,
        comp.comp_2_count,
        comp.comp_3_count,
        comp.comp_4_count,
        comp.comp_car_count,
        reach.lts1_len,
        reach.lts2_len,
        reach.lts3_len,
        reach.lts4_len,
        reach.car_len
    FROM
        density.density_h3 dens
        LEFT JOIN fragmentation.comp_count_h3 comp ON dens.hex_id = comp.h3_id
        LEFT JOIN reach.hex_reach reach ON dens.hex_id = reach.hex_id
);

-- ALTER TABLE
--     fragmentation.component_length_h3
-- ADD
--     COLUMN component_per_length_all DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_length_1 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_length_2 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_length_3 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_length_4 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_length_car DOUBLE PRECISION;
-- ALTER TABLE
--     fragmentation.component_length_h3
-- ADD
--     COLUMN component_per_dens_all DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_dens_1 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_dens_2 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_dens_3 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_dens_4 DOUBLE PRECISION,
-- ADD
--     COLUMN component_per_dens_car DOUBLE PRECISION;
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_length_all = comp_all_count / total_network_length
-- WHERE
--     (
--         total_network_length > 0
--         AND total_network_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_length_1 = comp_1_count / lts_1_length
-- WHERE
--     (
--         lts_1_length > 0
--         AND lts_1_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_length_2 = comp_2_count / lts_1_2_length
-- WHERE
--     (
--         lts_1_2_length > 0
--         AND lts_1_2_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_length_3 = comp_3_count / lts_1_3_length
-- WHERE
--     (
--         lts_1_3_length > 0
--         AND lts_1_3_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_length_4 = comp_4_count / lts_1_4_length
-- WHERE
--     (
--         lts_1_4_length > 0
--         AND lts_1_4_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_length_car = comp_car_count / total_car_length
-- WHERE
--     (
--         total_car_length > 0
--         AND total_car_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_dens_all = comp_all_count / total_network_dens
-- WHERE
--     (
--         total_network_length > 0
--         AND total_network_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_dens_1 = comp_1_count / lts_1_dens
-- WHERE
--     (
--         lts_1_length > 0
--         AND lts_1_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_dens_2 = comp_2_count / lts_1_2_dens
-- WHERE
--     (
--         lts_1_2_length > 0
--         AND lts_1_2_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_dens_3 = comp_3_count / lts_1_3_dens
-- WHERE
--     (
--         lts_1_3_length > 0
--         AND lts_1_3_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_dens_4 = comp_4_count / lts_1_4_dens
-- WHERE
--     (
--         lts_1_4_length > 0
--         AND lts_1_4_length IS NOT NULL
--     );
-- UPDATE
--     fragmentation.component_length_h3
-- SET
--     component_per_dens_car = comp_car_count / total_car_dens
-- WHERE
--     (
--         total_car_length > 0
--         AND total_car_length IS NOT NULL
--     );