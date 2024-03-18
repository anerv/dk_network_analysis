ALTER TABLE
    edges
ADD
    COLUMN road_infrastructure_length FLOAT DEFAULT NULL,
ADD
    COLUMN bike_infrastructure_length FLOAT DEFAULT NULL,
ADD
    COLUMN pedestrian_infrastructure_length FLOAT DEFAULT NULL;

UPDATE
    edges
SET
    road_infrastructure_length = CASE
        WHEN (
            lts_access IN (1, 2, 3, 4, 7)
            AND car_traffic IS TRUE
            AND car_oneway IS FALSE
        ) THEN ST_Length(geometry) * 2
        WHEN (
            lts_access IN (1, 2, 3, 4, 7)
            AND car_traffic IS TRUE
            AND car_oneway IS TRUE
        ) THEN ST_Length(geometry)
        ELSE NULL
    END;

-- todo: also fill out bike path network (lts XXX)
UPDATE
    edges
SET
    bike_infrastructure_length = CASE
        WHEN lts_access = 5 THEN ST_Length(geometry) * 2
        WHEN lts_access IN (1, 2, 3, 4)
        AND bikeinfra_oneway IS FALSE THEN ST_Length(geometry) * 2
        WHEN lts_access IN (1, 2, 3, 4)
        AND bikeinfra_oneway IS TRUE THEN ST_Length(geometry)
        ELSE NULL
    END;

UPDATE
    edges
SET
    pedestrian_infrastructure_length = CASE
        WHEN lts_access = 6 THEN ST_Length(geometry) * 2
        ELSE NULL
    END;

-- one direction counts as one unit:
-- if a road is oneway infra length = length
-- if a road is not oneway infra length = length * 2
-- if a road has bike in one side or bike infra is one way --> infra length = length
-- if not one way or both sides --> infra length = length * 2
--
-- TODO: make sure columns are filled out for all edges with lts and all edges with cycling/cars allowed
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
'Bike edges missing infrastructure length value';

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
        AND LTS IN (1, 2, 3, 4, 5);

ASSERT lts_infra_count = 0,
'LTS edges missing infrastructure length value';

END $$;

DO $$
DECLARE
    car_infra_count INT;

BEGIN
    SELECT
        COUNT(*) INTO car_infra_count
    FROM
        edges
    WHERE
        road_infrastructure_length IS NULL
        AND car_traffic IS TRUE;

ASSERT car_infra_count = 0,
'Road edges missing infrastructure length value';

END $$;