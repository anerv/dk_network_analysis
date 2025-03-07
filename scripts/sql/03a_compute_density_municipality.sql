DROP SCHEMA IF EXISTS density CASCADE;

CREATE SCHEMA density;

CREATE INDEX IF NOT EXISTS lts_access_ix ON edges (lts_access);

-- OBS - GAPS NOT INCLUDED IN THE CALCULATION - ONLY USED FOR FRAGMENTATION/REACHABILITY ANALYSIS
CREATE TABLE IF NOT EXISTS density.density_municipality AS WITH lts_1 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_1_length,
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
        SUM(infra_length) / 1000 AS lts_2_length,
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
        SUM(infra_length) / 1000 AS lts_3_length,
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
        SUM(infra_length) / 1000 AS lts_4_length,
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
        SUM(infra_length) / 1000 AS lts_5_length,
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
        SUM(infra_length) / 1000 AS lts_6_length,
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
        SUM(infra_length) / 1000 AS lts_7_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (7)
    GROUP BY
        municipality
),
lts_8 AS (
    SELECT
        SUM(infra_length) / 1000 AS lts_8_length,
        municipality
    FROM
        edges
    WHERE
        lts_access IN (8)
    GROUP BY
        municipality
),
total_car AS (
    SELECT
        SUM(infra_length) / 1000 AS total_car_length,
        municipality
    FROM
        edges
    WHERE
        car_traffic IS TRUE
        AND lts_access IN (1, 2, 3, 4, 7)
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
    total_car.total_car_length,
    municipalities.geometry
FROM
    municipalities
    LEFT JOIN lts_1 ON municipalities.navn = lts_1.municipality
    LEFT JOIN lts_2 ON municipalities.navn = lts_2.municipality
    LEFT JOIN lts_3 ON municipalities.navn = lts_3.municipality
    LEFT JOIN lts_4 ON municipalities.navn = lts_4.municipality
    LEFT JOIN lts_5 ON municipalities.navn = lts_5.municipality
    LEFT JOIN lts_6 ON municipalities.navn = lts_6.municipality
    LEFT JOIN lts_7 ON municipalities.navn = lts_7.municipality
    LEFT JOIN total_car ON municipalities.navn = total_car.municipality;

-- REMOVE CHRISTIANSØ
DELETE FROM
    density.density_municipality
WHERE
    municipality IS NULL;

ALTER TABLE
    density.density_municipality
ADD
    COLUMN IF NOT EXISTS total_network_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_length DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_2_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_3_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_4_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_7_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_car_dens DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_network_dens DOUBLE PRECISION DEFAULT NULL;

UPDATE
    density.density_municipality
SET
    lts_1_length = 0
WHERE
    lts_1_length IS NULL;

UPDATE
    density.density_municipality
SET
    lts_2_length = 0
WHERE
    lts_2_length IS NULL;

UPDATE
    density.density_municipality
SET
    lts_3_length = 0
WHERE
    lts_3_length IS NULL;

UPDATE
    density.density_municipality
SET
    lts_4_length = 0
WHERE
    lts_4_length IS NULL;

UPDATE
    density.density_municipality
SET
    lts_7_length = 0
WHERE
    lts_7_length IS NULL;

-- DO NOT INCLUDE PEDESTRIAN, PATHS NOT SUITABLE FOR EVERYDAY CYCLING, AND NO CYCLING
UPDATE
    density.density_municipality
SET
    total_network_length = lts_1_length + lts_2_length + lts_3_length + lts_4_length + lts_7_length;

UPDATE
    density.density_municipality
SET
    lts_1_2_length = lts_1_length + lts_2_length,
    lts_1_3_length = lts_1_length + lts_2_length + lts_3_length,
    lts_1_4_length = lts_1_length + lts_2_length + lts_3_length + lts_4_length;

UPDATE
    density.density_municipality
SET
    lts_1_dens = lts_1_length / (ST_Area(geometry) / 1000000),
    lts_2_dens = lts_2_length / (ST_Area(geometry) / 1000000),
    lts_3_dens = lts_3_length / (ST_Area(geometry) / 1000000),
    lts_4_dens = lts_4_length / (ST_Area(geometry) / 1000000),
    lts_7_dens = lts_7_length / (ST_Area(geometry) / 1000000),
    lts_1_2_dens = (lts_1_length + lts_2_length) / (ST_Area(geometry) / 1000000),
    lts_1_3_dens = (lts_1_length + lts_2_length + lts_3_length) / (ST_Area(geometry) / 1000000),
    lts_1_4_dens = (
        lts_1_length + lts_2_length + lts_3_length + lts_4_length
    ) / (ST_Area(geometry) / 1000000),
    total_car_dens = (total_car_length) / (ST_Area(geometry) / 1000000),
    total_network_dens = (total_network_length) / (ST_Area(geometry) / 1000000);

-- CALCULATE RELATIVE LENGTH
ALTER TABLE
    density.density_municipality
ADD
    COLUMN IF NOT EXISTS lts_1_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_2_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_3_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_1_4_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_7_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS total_car_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_2_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_3_pct DOUBLE PRECISION DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS lts_4_pct DOUBLE PRECISION DEFAULT NULL;

UPDATE
    density.density_municipality
SET
    lts_1_pct = lts_1_length / total_network_length * 100,
    lts_2_pct = lts_2_length / total_network_length * 100,
    lts_3_pct = lts_3_length / total_network_length * 100,
    lts_4_pct = lts_4_length / total_network_length * 100,
    lts_1_2_pct = (lts_1_length + lts_2_length) / total_network_length * 100,
    lts_1_3_pct = (lts_1_length + lts_2_length + lts_3_length) / total_network_length * 100,
    lts_1_4_pct = (
        lts_1_length + lts_2_length + lts_3_length + lts_4_length
    ) / total_network_length * 100,
    lts_7_pct = lts_7_length / total_network_length * 100,
    total_car_pct = total_car_length / total_network_length * 100;

DO $$
DECLARE
    miscalculated INT;

BEGIN
    SELECT
        COUNT(*) INTO miscalculated
    FROM
        density.density_municipality
    WHERE
        lts_1_2_dens < lts_1_dens
        OR lts_1_3_dens < lts_1_2_dens
        OR lts_1_4_dens < lts_1_3_dens
        OR total_network_dens < lts_1_4_dens;

ASSERT miscalculated = 0,
'Problem with network density calculation. Check if the network density is calculated correctly.';

END $$;