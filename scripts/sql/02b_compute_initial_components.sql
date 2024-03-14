ALTER TABLE
    kbh
ADD
    COLUMN IF NOT EXISTS component_all BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_1 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_2 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_3 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_4 BIGINT DEFAULT NULL;

-- ADD
--     COLUMN IF NOT EXISTS component_5 BIGINT DEFAULT NULL,
-- ADD
--     COLUMN IF NOT EXISTS component_6 BIGINT DEFAULT NULL,
-- ADD
--     COLUMN IF NOT EXISTS component_7 BIGINT DEFAULT NULL,
-- ADD
--     COLUMN IF NOT EXISTS component_0 BIGINT DEFAULT NULL;
DROP TABLE IF EXISTS components;

DROP TABLE IF EXISTS components_1;

DROP TABLE IF EXISTS components_2;

DROP TABLE IF EXISTS components_3;

DROP TABLE IF EXISTS components_4;

CREATE TABLE components AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM kbh'
    );

CREATE TABLE components_1 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access = 1'
    );

CREATE TABLE components_2 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access IN (1,2)'
    );

CREATE TABLE components_3 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access IN (1,2,3)'
    );

CREATE TABLE components_4 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access IN (1,2,3,4)'
    );

UPDATE
    kbh e
SET
    component_all = component
FROM
    components co
WHERE
    e.source = co.node;

UPDATE
    kbh e
SET
    component_1 = component
FROM
    components_1 co
WHERE
    e.source = co.node
    AND lts_access = 1;

UPDATE
    kbh e
SET
    component_2 = component
FROM
    components_2 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2);

;

UPDATE
    kbh e
SET
    component_3 = component
FROM
    components_3 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2, 3);

UPDATE
    kbh e
SET
    component_4 = component
FROM
    components_4 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2, 3, 4);

-- CREATE TABLE component_5 AS
-- SELECT
--     *
-- FROM
--     pgr_connectedComponents(
--         'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access = 5'
--     );
-- ---- **** -----
-- CREATE TABLE component_6 AS
-- SELECT
--     *
-- FROM
--     pgr_connectedComponents(
--         'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access = 6'
--     );
-- CREATE TABLE component_7 AS
-- SELECT
--     *
-- FROM
--     pgr_connectedComponents(
--         'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access = 7'
--     );
-- CREATE TABLE component_0 AS
-- SELECT
--     *
-- FROM
--     pgr_connectedComponents(
--         'SELECT id, source, target, cost, reverse_cost FROM kbh WHERE lts_access = 0'
--     );
DROP TABLE IF EXISTS components;

DROP TABLE IF EXISTS components_1;

DROP TABLE IF EXISTS components_2;

DROP TABLE IF EXISTS components_3;

DROP TABLE IF EXISTS components_4;