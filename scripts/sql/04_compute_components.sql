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

DROP TABLE IF EXISTS components;

DROP TABLE IF EXISTS components_1;

DROP TABLE IF EXISTS components_1_2;

DROP TABLE IF EXISTS components_1_3;

DROP TABLE IF EXISTS components_1_4;

DROP TABLE IF EXISTS components_car;

CREATE TABLE components AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2,3,4,7) OR lts_1_gap IS TRUE OR lts_2_gap IS TRUE OR lts_3_gap IS TRUE OR lts_4_gap IS TRUE'
    );

CREATE TABLE components_1 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 1 OR lts_1_gap IS TRUE'
    );

CREATE TABLE components_2 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2) OR lts_1_gap IS TRUE or lts_2_gap IS TRUE'
    );

CREATE TABLE components_3 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2,3) OR lts_1_gap IS TRUE or lts_2_gap IS TRUE or lts_3_gap IS TRUE'
    );

CREATE TABLE components_4 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access IN (1,2,3,4) OR lts_1_gap IS TRUE or lts_2_gap IS TRUE or lts_3_gap IS TRUE or lts_4_gap IS TRUE'
    );

CREATE TABLE components_car AS (
    SELECT
        *
    FROM
        pgr_connectedComponents(
            'SELECT id, source, target, cost, reverse_cost FROM edges WHERE car_traffic IS TRUE'
        )
);

UPDATE
    edges e
SET
    component_all = component
FROM
    components co
WHERE
    e.source = co.node;

UPDATE
    edges e
SET
    component_1 = component
FROM
    components_1 co
WHERE
    e.source = co.node
    AND lts_access = 1
    OR lts_1_gap IS TRUE;

UPDATE
    edges e
SET
    component_1_2 = component
FROM
    components_2 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE;

;

UPDATE
    edges e
SET
    component_1_3 = component
FROM
    components_3 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2, 3)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE
    OR lts_3_gap IS TRUE;

UPDATE
    edges e
SET
    component_1_4 = component
FROM
    components_4 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2, 3, 4)
    OR lts_1_gap IS TRUE
    OR lts_2_gap IS TRUE
    OR lts_3_gap IS TRUE
    OR lts_4_gap IS TRUE;

UPDATE
    edges e
SET
    component_car = component
FROM
    components_car co
WHERE
    e.source = co.node
    AND car_traffic IS TRUE;

DROP TABLE IF EXISTS components;

DROP TABLE IF EXISTS components_1;

DROP TABLE IF EXISTS components_1_2;

DROP TABLE IF EXISTS components_1_3;

DROP TABLE IF EXISTS components_1_4;

DROP TABLE IF EXISTS components_car;