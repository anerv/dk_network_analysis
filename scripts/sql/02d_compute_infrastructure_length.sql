ALTER TABLE
    edges
ADD
    COLUMN IF NOT EXISTS bike_infrastructure_length FLOAT DEFAULT NULL;

UPDATE
    edges
SET
    bike_infrastructure_length = CASE
        WHEN (
            bikeinfra_both_sides IS TRUE
            AND cycling_allowed IS TRUE
        ) THEN ST_Length(geometry) * 2
        WHEN (
            bikeinfra_both_sides IS FALSE
            AND cycling_allowed IS TRUE
        ) THEN ST_Length(geometry)
        ELSE NULL
    END;

DO $$
DECLARE
    bike_infra_count INT;

BEGIN
    SELECT
        COUNT(*) INTO bike_infra_count
    FROM
        edges
    WHERE
        bike_infrastructure_length IS NULL
        AND cycling_allowed IS TRUE;

ASSERT bike_infra_count = 0,
'Bike infra edges missing infrastructure length value';

END $$;

DO $$
DECLARE
    lts_infra_count INT;

BEGIN
    SELECT
        COUNT(*) INTO lts_infra_count
    FROM
        edges
    WHERE
        bike_infrastructure_length IS NULL
        AND lts_access IN (1, 2, 3, 4, 5);

ASSERT lts_infra_count = 0,
'LTS edges missing infrastructure length value';

END $$;