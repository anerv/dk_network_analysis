DROP TABLE IF EXISTS fragmentation.joined,
fragmentation.joined2,
fragmentation.socio_largest_component;

CREATE INDEX IF NOT EXISTS hex_largset_geom_ix ON fragmentation.hex_largest_components USING GIST (geometry);

CREATE TABLE fragmentation.joined AS (
    SELECT
        hc. *,
        s.id,
        s.geometry AS socio_geom
    FROM
        fragmentation.hex_largest_components hc
        JOIN socio s ON ST_Intersects(s.geometry, ST_Centroid(hc.geometry))
);

CREATE TABLE fragmentation.joined2 AS WITH unjoined AS (
    SELECT
        *
    FROM
        socio
    WHERE
        id NOT IN (
            SELECT
                DISTINCT id
            FROM
                fragmentation.joined
        )
)
SELECT
    hc. *,
    s.id,
    s.geometry AS socio_geom
FROM
    fragmentation.hex_largest_components hc
    JOIN unjoined s ON ST_Intersects(s.geometry, hc.geometry);

INSERT INTO
    fragmentation.joined (
        SELECT
            *
        FROM
            fragmentation.joined2
        WHERE
            id NOT IN (
                SELECT
                    DISTINCT id
                FROM
                    fragmentation.joined
            )
    );

CREATE TABLE fragmentation.socio_largest_component AS
SELECT
    j.id,
    AVG(j.component_length_1) AS lts_1_largest_component_average,
    AVG(j.component_length_1_2) AS lts_1_2_largest_component_average,
    AVG(j.component_length_1_3) AS lts_1_3_largest_component_average,
    AVG(j.component_length_1_4) AS lts_1_4_largest_component_average,
    AVG(j.component_length_car) AS car_largest_component_average,
    MIN(j.component_length_1) AS lts_1_largest_component_min,
    MIN(j.component_length_1_2) AS lts_1_2_largest_component_min,
    MIN(j.component_length_1_3) AS lts_1_3_largest_component_min,
    MIN(j.component_length_1_4) AS lts_1_4_largest_component_min,
    MIN(j.component_length_car) AS car_largest_component_min,
    MAX(j.component_length_1) AS lts_1_largest_component_max,
    MAX(j.component_length_1_2) AS lts_1_2_largest_component_max,
    MAX(j.component_length_1_3) AS lts_1_3_largest_component_max,
    MAX(j.component_length_1_4) AS lts_1_4_largest_component_max,
    MAX(j.component_length_car) AS car_largest_component_max,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.component_length_1
    ) AS lts1_largest_component_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.component_length_1_2
    ) AS lts_1_2_largest_component_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.component_length_1_3
    ) AS lts_1_3_largest_component_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.component_length_1_4
    ) AS lts_1_4_largest_component_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.component_length_car
    ) AS car_largest_component_median
FROM
    fragmentation.joined j
GROUP BY
    j.id;

ALTER TABLE
    fragmentation.socio_largest_component
ADD
    COLUMN IF NOT EXISTS geometry geometry;

UPDATE
    fragmentation.socio_largest_component
SET
    geometry = s.geometry
FROM
    socio s
WHERE
    fragmentation.socio_largest_component.id = s.id;

DROP TABLE IF EXISTS fragmentation.joined,
fragmentation.joined2;