ALTER TABLE
    edges
ADD
    COLUMN IF NOT EXISTS component_all BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_1 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_2 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_3 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_4 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_5 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_6 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_7 BIGINT DEFAULT NULL,
ADD
    COLUMN IF NOT EXISTS component_0 BIGINT DEFAULT NULL,
;

DROP TABLE IF EXISTS components;

CREATE TABLE components AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges'
    );

UPDATE
    edges e
SET
    component_all = component
FROM
    components co
WHERE
    e.source = co.node;

CREATE TABLE component_1 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 1'
    );

CREATE TABLE component_2 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 2'
    );

CREATE TABLE component_3 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 3'
    );

CREATE TABLE component_4 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 4'
    );

CREATE TABLE component_5 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 5'
    );

CREATE TABLE component_6 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 6'
    );

CREATE TABLE component_7 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 7'
    );

CREATE TABLE component_0 AS
SELECT
    *
FROM
    pgr_connectedComponents(
        'SELECT id, source, target, cost, reverse_cost FROM edges WHERE lts_access = 0'
    );