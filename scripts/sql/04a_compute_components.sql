DROP SCHEMA IF EXISTS fragmentation CASCADE;

CREATE schema fragmentation;

DROP TABLE IF EXISTS fragmentation.components;

DROP TABLE IF EXISTS fragmentation.components_1;

DROP TABLE IF EXISTS fragmentation.components_2;

DROP TABLE IF EXISTS fragmentation.components_3;

DROP TABLE IF EXISTS fragmentation.components_4;

DROP TABLE IF EXISTS fragmentation.components_car;

ALTER TABLE
    edges DROP COLUMN IF EXISTS component_all,
    DROP COLUMN IF EXISTS component_1,
    DROP COLUMN IF EXISTS component_1_2,
    DROP COLUMN IF EXISTS component_1_3,
    DROP COLUMN IF EXISTS component_1_4,
    DROP COLUMN IF EXISTS component_car;

ALTER TABLE
    edges
ADD
    COLUMN IF NOT EXISTS component_all BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_1 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_1_2 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_1_3 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_1_4 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_car BIGINT DEFAULT NULL;

DROP TABLE IF EXISTS fragmentation.components;

DROP TABLE IF EXISTS fragmentation.components_1;

DROP TABLE IF EXISTS components_1_2;

DROP TABLE IF EXISTS components_1_3;

DROP TABLE IF EXISTS components_1_4;

DROP TABLE IF EXISTS fragmentation.components_car;

CREATE TABLE fragmentation.components AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2,3,4,7) OR lts_1_gap IS TRUE OR lts_2_gap IS TRUE OR lts_3_gap IS TRUE OR lts_4_gap IS TRUE'
    );

CREATE TABLE fragmentation.components_1 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 1 OR lts_1_gap IS TRUE'
    );

CREATE TABLE fragmentation.components_2 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2) OR lts_1_gap IS TRUE or lts_2_gap IS TRUE'
    );

CREATE TABLE fragmentation.components_3;

AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2,3) OR lts_1_gap IS TRUE or lts_2_gap IS TRUE or lts_3_gap IS TRUE'
    );

CREATE TABLE fragmentation.components_4;

AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2,3,4) OR lts_1_gap IS TRUE or lts_2_gap IS TRUE or lts_3_gap IS TRUE or lts_4_gap IS TRUE'
    );

CREATE TABLE fragmentation.components_car;

AS (
    SELECT
        *
    FROM
        pgr_connectedComponents(
            'SELECT id, source, target, cost, reverse_cost FROM edges WHERE car_traffic IS TRUE AND lts_access IN (1,2,3,4,7)' -- Should we include gaps here?
        )
);

UPDATE
    edges e
SET
    component_all = component
FROM
    fragmentation.components co
WHERE
    e.source = co.node
    AND (
        lts_access IN (1, 2, 3, 4, 7)
        OR lts_1_gap IS TRUE
        OR lts_2_gap IS TRUE
        OR lts_3_gap IS TRUE
        OR lts_4_gap IS TRUE
    );

UPDATE
    edges e
SET
    component_1 = component
FROM
    fragmentation.components_1 co
WHERE
    e.source = co.node
    AND (
        lts_access = 1
        OR lts_1_gap IS TRUE
    );

UPDATE
    edges e
SET
    component_1_2 = component
FROM
    fragmentation.components_2 co
WHERE
    e.source = co.node
    AND (
        lts_access IN (1, 2)
        OR lts_1_gap IS TRUE
        OR lts_2_gap IS TRUE
    );

UPDATE
    edges e
SET
    component_1_3 = component
FROM
    fragmentation.components_3;

co
WHERE
    e.source = co.node
    AND (
        lts_access IN (1, 2, 3)
        OR lts_1_gap IS TRUE
        OR lts_2_gap IS TRUE
        OR lts_3_gap IS TRUE
    );

UPDATE
    edges e
SET
    component_1_4 = component
FROM
    fragmentation.components_4;

co
WHERE
    e.source = co.node
    AND (
        lts_access IN (1, 2, 3, 4)
        OR lts_1_gap IS TRUE
        OR lts_2_gap IS TRUE
        OR lts_3_gap IS TRUE
        OR lts_4_gap IS TRUE
    );

UPDATE
    edges e
SET
    component_car = component
FROM
    fragmentation.components_car;

co
WHERE
    e.source = co.node
    AND car_traffic IS TRUE
    AND lts_access IN (1, 2, 3, 4, 7);

--- CHECK COMPONENT COMPUTATION -- 
-- CHECK FOR TOO MANY COMP VALUES
DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        lts_access <> 1
        AND lts_1_gap IS NULL
        AND component_1 IS NOT NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        lts_access NOT IN (1, 2)
        AND lts_1_gap IS NULL
        AND lts_2_gap IS NULL
        AND component_1_2 IS NOT NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1_2';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        lts_access NOT IN (1, 2, 3)
        AND lts_1_gap IS NULL
        AND lts_2_gap IS NULL
        AND lts_3_gap IS NULL
        AND component_1_3 IS NOT NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1_3';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        lts_access NOT IN (1, 2, 3, 4)
        AND lts_1_gap IS NULL
        AND lts_2_gap IS NULL
        AND lts_3_gap IS NULL
        AND lts_4_gap IS NULL
        AND component_1_4 IS NOT NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1_4';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        lts_access NOT IN (1, 2, 3, 4, 7)
        AND lts_1_gap IS NULL
        AND lts_2_gap IS NULL
        AND lts_3_gap IS NULL
        AND lts_4_gap IS NULL
        AND component_all IS NOT NULL;

ASSERT comp_check = 0,
'Problem with component calculation for component all';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        (
            car_traffic IS FALSE
            OR lts_access NOT IN (1, 2, 3, 4, 7)
        )
        AND component_car IS NOT NULL;

ASSERT comp_check = 0,
'Problem with component calculation for car fragmentation.components';

END $$;

----- CHECK FOR MISSING COMP VALUES
DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        (
            lts_access = 1
            OR lts_1_gap IS TRUE
        )
        AND component_1 IS NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        (
            lts_access IN (1, 2)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
        )
        AND component_1_2 IS NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1_2';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        (
            lts_access IN (1, 2, 3)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
        )
        AND component_1_3 IS NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1_3';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        (
            lts_access IN (1, 2, 3, 4)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
            OR lts_4_gap IS TRUE
        )
        AND component_1_4 IS NULL;

ASSERT comp_check = 0,
'Problem with component calculation for LTS 1_4';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        (
            lts_access IN (1, 2, 3, 4, 7)
            OR lts_1_gap IS TRUE
            OR lts_2_gap IS TRUE
            OR lts_3_gap IS TRUE
            OR lts_4_gap IS TRUE
        )
        AND component_all IS NULL;

ASSERT comp_check = 0,
'Problem with component calculation for component all';

END $$;

DO $$
DECLARE
    comp_check INT;

BEGIN
    SELECT
        COUNT(*) INTO comp_check
    FROM
        edges
    WHERE
        car_traffic IS TRUE
        AND lts_access IN (1, 2, 3, 4, 7)
        AND component_car IS NULL;

ASSERT comp_check = 0,
'Problem with component calculation for car fragmentation.components';

END $$;

DROP TABLE IF EXISTS fragmentation.components;

DROP TABLE IF EXISTS fragmentation.components_1;

DROP TABLE IF EXISTS fragmentation.components_2;

DROP TABLE IF EXISTS fragmentation.components_3;

DROP TABLE IF EXISTS fragmentation.components_4;

DROP TABLE IF EXISTS fragmentation.components_car;