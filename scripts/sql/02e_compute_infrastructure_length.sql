ALTER TABLE
    edges
ADD
    COLUMN IF NOT EXISTS infra_length FLOAT DEFAULT NULL;

UPDATE
    edges
SET
    infra_length = ST_Length(geometry);

-- ADD
--     COLUMN IF NOT EXISTS bike_length FLOAT DEFAULT NULL,
-- ADD
--     COLUMN IF NOT EXISTS car_length FLOAT DEFAULT NULL;
-- UPDATE
--     edges
-- SET
--     bike_length = ST_Length(geometry)
-- WHERE
--     cycling_allowed IS TRUE;
-- UPDATE
--     edges
-- SET
--     car_length = ST_Length(geometry)
-- WHERE
--     car_traffic IS TRUE;
-- UPDATE
--     edges
-- SET
--     bike_length = CASE
--         WHEN (
--             bikeinfra_both_sides IS TRUE
--             AND cycling_allowed IS TRUE
--         ) THEN ST_Length(geometry) * 2
--         WHEN (
--             bikeinfra_both_sides IS FALSE
--             AND cycling_allowed IS TRUE
--         ) THEN ST_Length(geometry)
--         ELSE NULL
--     END;
-- DO $$
-- DECLARE
--     bike_len_count INT;
-- BEGIN
--     SELECT
--         COUNT(*) INTO bike_len_count
--     FROM
--         edges
--     WHERE
--         bike_length IS NULL
--         AND cycling_allowed IS TRUE;
-- ASSERT bike_len_count = 0,
-- 'Bike infra edges missing infrastructure length value';
-- END $$;
-- DO $$
-- DECLARE
--     car_len_count INT;
-- BEGIN
--     SELECT
--         COUNT(*) INTO car_len_count
--     FROM
--         edges
--     WHERE
--         car_length IS NULL
--         AND car_traffic IS TRUE;
-- ASSERT car_len_count = 0,
-- 'Car edges missing infrastructure length value';
-- END $$;
-- DO $$
-- DECLARE
--     lts_infra_count INT;
-- BEGIN
--     SELECT
--         COUNT(*) INTO lts_infra_count
--     FROM
--         edges
--     WHERE
--         bike_length IS NULL
--         AND lts_access IN (1, 2, 3, 4, 5);
-- ASSERT lts_infra_count = 0,
-- 'LTS edges missing infrastructure length value';
-- END $$;