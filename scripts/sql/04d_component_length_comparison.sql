CREATE VIEW component_length_muni AS (
    SELECT
        dens.municipality,
        dens.lts_1_length,
        dens.lts_2_length,
        dens.lts_3_length,
        dens.lts_4_length,
        dens.total_car_length,
        dens.total_network_length,
        dens.lts_1_dens,
        dens.lts_1_2_dens,
        dens.lts_1_3_dens,
        dens.lts_1_4_dens,
        dens.total_car_dens,
        dens.total_network_dens,
        den.geometry,
        comp.comp_all_count,
        comp.comp_1_count,
        comp.comp_2_count,
        comp.comp_3_count,
        comp.comp_4_count,
        comp.comp_car_count
    FROM
        density_municipality dens
        JOIN comp_count_muni comp USING (municipality)
);

CREATE VIEW component_length_socio AS (
    SELECT
        dens.municipality,
        dens.lts_1_length,
        dens.lts_2_length,
        dens.lts_3_length,
        dens.lts_4_length,
        dens.total_car_length,
        dens.total_network_length,
        dens.lts_1_dens,
        dens.lts_1_2_dens,
        dens.lts_1_3_dens,
        dens.lts_1_4_dens,
        dens.total_car_dens,
        dens.total_network_dens,
        den.geometry,
        comp.comp_all_count,
        comp.comp_1_count,
        comp.comp_2_count,
        comp.comp_3_count,
        comp.comp_4_count,
        comp.comp_car_count
    FROM
        density_municipality dens
        JOIN comp_count_muni comp USING (municipality)
);

CREATE VIEW component_length_h3 AS (
    SELECT
        dens.municipality,
        dens.lts_1_length,
        dens.lts_2_length,
        dens.lts_3_length,
        dens.lts_4_length,
        dens.total_car_length,
        dens.total_network_length,
        dens.lts_1_dens,
        dens.lts_1_2_dens,
        dens.lts_1_3_dens,
        dens.lts_1_4_dens,
        dens.total_car_dens,
        dens.total_network_dens,
        den.geometry,
        comp.comp_all_count,
        comp.comp_1_count,
        comp.comp_2_count,
        comp.comp_3_count,
        comp.comp_4_count,
        comp.comp_car_count
    FROM
        density_municipality dens
        JOIN comp_count_muni comp USING (municipality)
);