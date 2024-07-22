ALTER TABLE
    gap_threshold_analysis.edges
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

DROP TABLE IF EXISTS gap_threshold_analysis.components;

DROP TABLE IF EXISTS gap_threshold_analysis.components_1;

DROP TABLE IF EXISTS gap_threshold_analysis.components_2;

DROP TABLE IF EXISTS gap_threshold_analysis.components_3;

DROP TABLE IF EXISTS gap_threshold_analysis.components_4;

CREATE TABLE gap_threshold_analysis.components AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges'
    );

CREATE TABLE gap_threshold_analysis.components_1 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges WHERE lts_access = 1'
    );

CREATE TABLE gap_threshold_analysis.components_2 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges WHERE lts_access IN (1,2)'
    );

CREATE TABLE gap_threshold_analysis.components_3 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges WHERE lts_access IN (1,2,3)'
    );

CREATE TABLE gap_threshold_analysis.components_4 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges WHERE lts_access IN (1,2,3,4)'
    );

UPDATE
    gap_threshold_analysis.edges e
SET
    component_all = component
FROM
    gap_threshold_analysis.components co
WHERE
    e.source = co.node;

UPDATE
    gap_threshold_analysis.edges e
SET
    component_1 = component
FROM
    gap_threshold_analysis.components_1 co
WHERE
    e.source = co.node
    AND lts_access = 1;

UPDATE
    gap_threshold_analysis.edges e
SET
    component_2 = component
FROM
    gap_threshold_analysis.components_2 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2);

UPDATE
    gap_threshold_analysis.edges e
SET
    component_3 = component
FROM
    gap_threshold_analysis.components_3 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2, 3);

UPDATE
    gap_threshold_analysis.edges e
SET
    component_4 = component
FROM
    gap_threshold_analysis.components_4 co
WHERE
    e.source = co.node
    AND lts_access IN (1, 2, 3, 4);