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

UPDATE
    reach.reach_component_length_h3
SET
    lts1_len = lts1_len / 1000,
    lts2_len = lts2_len / 1000,
    lts3_len = lts3_len / 1000,
    lts4_len = lts4_len / 1000,
    car_len = car_len / 1000;