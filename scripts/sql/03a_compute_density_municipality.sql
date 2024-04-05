DROP TABLE IF EXISTS density_municipality;

CREATE INDEX IF NOT EXISTS lts_access_ix ON edges (lts_access);

CREATE TABLE IF NOT EXISTS density_municipality AS WITH lts_1 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_1_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (1)
    GROUP BY
        municipality
),
lts_2 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_2_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (2)
    GROUP BY
        municipality
),
lts_3 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_3_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (3)
    GROUP BY
        municipality
),
lts_4 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_4_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (4)
    GROUP BY
        municipality
),
lts_5 AS (
    SELECT
        SUM(bike_length) / 1000 AS lts_5_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (5)
    GROUP BY
        municipality
),
lts_6 AS (
    SELECT
        SUM(ST_Length(geometry)) / 1000 AS lts_6_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (6)
    GROUP BY
        municipality
),
lts_7 AS (
    SELECT
        SUM(ST_Length(geometry)) / 1000 AS lts_7_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (7)
    GROUP BY
        municipality
),
-- below is computed to consider situations where bike infra is mapped separately from the road.
-- sometimes cycling is still not mapped as cycling not allowed on the main road - will end up double counting?
-- but! cannot know which lts to subtract from.
-- bike_infra_by_road AS (
--     SELECT
--         SUM(bike_length) / 1000 AS bike_infra_by_road,
--         municipality
--     FROM
--         edges
--     WHERE
--         (
--             highway IN ('cycleway', 'crossing')
--             AND bicycle_category IN ('cycletrack', 'crossing')
--             OR (
--                 bicycle_infrastructure_osm IS FALSE
--                 AND bicycle_infrastructure_final IS TRUE
--                 AND matched IS TRUE
--                 AND highway = 'path'
--             )
--         )
--     GROUP BY
--         municipality
-- ),
total_car AS (
    SELECT
        SUM(ST_Length(geometry)) / 1000 AS total_car,
        municipality
    FROM
        edges
    WHERE
        car_traffic IS TRUE
    GROUP BY
        municipality
)
SELECT
    lts_1.municipality,
    lts_1.lts_1_length,
    lts_2.lts_2_length,
    lts_3.lts_3_length,
    lts_4.lts_4_length,
    lts_5.lts_5_length,
    lts_6.lts_6_length,
    lts_7.lts_7_length,
    --bike_infra_by_road.bike_infra_by_road,
    total_car.total_car,
    adm_boundaries.geometry
FROM
    adm_boundaries
    LEFT JOIN lts_1 ON adm_boundaries.navn = lts_1.municipality
    LEFT JOIN lts_2 ON adm_boundaries.navn = lts_2.municipality
    LEFT JOIN lts_3 ON adm_boundaries.navn = lts_3.municipality
    LEFT JOIN lts_4 ON adm_boundaries.navn = lts_4.municipality
    LEFT JOIN lts_5 ON adm_boundaries.navn = lts_5.municipality
    LEFT JOIN lts_6 ON adm_boundaries.navn = lts_6.municipality
    LEFT JOIN lts_7 ON adm_boundaries.navn = lts_7.municipality --LEFT JOIN bike_infra_by_road ON adm_boundaries.navn = bike_infra_by_road.municipality
    LEFT JOIN total_car ON adm_boundaries.navn = total_car.municipality;

DELETE FROM
    density_municipality
WHERE
    municipality IS NULL;

ALTER TABLE
    density_municipality
ADD
    COLUMN IF NOT EXISTS lts_1_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_car_dens DOUBLE PRECISION DEFAULT NULL;

UPDATE
    density_municipality
SET
    lts_1_length = 0
WHERE
    lts_1_length IS NULL;

UPDATE
    density_municipality
SET
    lts_2_length = 0
WHERE
    lts_2_length IS NULL;

UPDATE
    density_municipality
SET
    lts_3_length = 0
WHERE
    lts_3_length IS NULL;

UPDATE
    density_municipality
SET
    lts_4_length = 0
WHERE
    lts_4_length IS NULL;

UPDATE
    density_municipality
SET
    lts_1_dens = lts_1_length / (ST_Area(geometry) / 1000000),
    lts_1_2_dens = (lts_1_length + lts_2_length) / (ST_Area(geometry) / 1000000),
    lts_1_3_dens = (lts_1_length + lts_2_length + lts_3_length) / (ST_Area(geometry) / 1000000),
    lts_1_4_dens = (
        lts_1_length + lts_2_length + lts_3_length + lts_4_length
    ) / (ST_Area(geometry) / 1000000),
    total_car_dens = (total_car) / (ST_Area(geometry) / 1000000);