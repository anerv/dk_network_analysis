CREATE VIEW component_length_muni AS (
    SELECT
        * -- only include necesssary columns (e.g. lts length, municipality, geometry)
    FROM
        density_municipality
        JOIN comp_count_muni USING (municipality)
);

CREATE VIEW component_length_socio AS (
    SELECT
        *
    FROM
        density_municipality
        JOIN comp_count_muni USING (municipality)
);

CREATE VIEW component_length_h3 AS (
    SELECT
        *
    FROM
        density_municipality
        JOIN comp_count_muni USING (municipality)
);