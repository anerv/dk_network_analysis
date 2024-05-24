-- ***** JOIN REACH TO ORIGINAL HEX GEOMETRIES *****
DROP TABLE IF EXISTS reach.hex_reach;

ALTER TABLE
    reach.lts_1_reach
ADD
    COLUMN IF NOT EXISTS hex_id VARCHAR;

ALTER TABLE
    reach.lts_2_reach
ADD
    COLUMN IF NOT EXISTS hex_id VARCHAR;

ALTER TABLE
    reach.lts_3_reach
ADD
    COLUMN IF NOT EXISTS hex_id VARCHAR;

ALTER TABLE
    reach.lts_4_reach
ADD
    COLUMN IF NOT EXISTS hex_id VARCHAR;

ALTER TABLE
    reach.car_reach
ADD
    COLUMN IF NOT EXISTS hex_id VARCHAR;

UPDATE
    reach.lts_1_reach
SET
    hex_id = h.hex_id
FROM
    reach.hex_lts_1 h
WHERE
    reach.lts_1_reach.start_node = h.node_id;

UPDATE
    reach.lts_2_reach
SET
    hex_id = h.hex_id
FROM
    reach.hex_lts_2 h
WHERE
    reach.lts_2_reach.start_node = h.node_id;

UPDATE
    reach.lts_3_reach
SET
    hex_id = h.hex_id
FROM
    reach.hex_lts_3 h
WHERE
    reach.lts_3_reach.start_node = h.node_id;

UPDATE
    reach.lts_4_reach
SET
    hex_id = h.hex_id
FROM
    reach.hex_lts_4 h
WHERE
    reach.lts_4_reach.start_node = h.node_id;

UPDATE
    reach.car_reach
SET
    hex_id = h.hex_id
FROM
    reach.hex_car h
WHERE
    reach.car_reach.start_node = h.node_id;

CREATE INDEX IF NOT EXISTS hex_grid_ix ON hex_grid (hex_id);

CREATE INDEX IF NOT EXISTS lts_1_reach_ix ON reach.lts_1_reach (hex_id);

CREATE INDEX IF NOT EXISTS lts_2_reach_ix ON reach.lts_2_reach (hex_id);

CREATE INDEX IF NOT EXISTS lts_3_reach_ix ON reach.lts_3_reach (hex_id);

CREATE INDEX IF NOT EXISTS lts_4_reach_ix ON reach.lts_4_reach (hex_id);

CREATE INDEX IF NOT EXISTS car_reach_ix ON reach.car_reach (hex_id);

CREATE TABLE reach.hex_reach AS
SELECT
    h.hex_id,
    h.geometry,
    l1.edge_length AS lts1_len,
    l2.edge_length AS lts2_len,
    l3.edge_length AS lts3_len,
    l4.edge_length AS lts4_len,
    ca.edge_length AS car_len
FROM
    hex_grid h
    LEFT JOIN reach.lts_1_reach l1 ON h.hex_id = l1.hex_id
    LEFT JOIN reach.lts_2_reach l2 ON h.hex_id = l2.hex_id
    LEFT JOIN reach.lts_3_reach l3 ON h.hex_id = l3.hex_id
    LEFT JOIN reach.lts_4_reach l4 ON h.hex_id = l4.hex_id
    LEFT JOIN reach.car_reach ca ON h.hex_id = ca.hex_id;

DO $$
DECLARE
    hex_reach_len INT;

DECLARE
    hex_grid_len INT;

BEGIN
    SELECT
        COUNT(*) INTO hex_reach_len
    FROM
        reach.hex_reach;

SELECT
    COUNT(*) INTO hex_grid_len
FROM
    hex_grid;

ASSERT hex_grid_len = hex_reach_len,
'Missing hex cells!';

END $$;

-- **** COMPUTE ABS DECREASE IN REACH FROM CAR TO LTS 4 etc. ****
ALTER TABLE
    reach.hex_reach
ADD
    COLUMN car_lts1_diff DECIMAL,
ADD
    COLUMN car_lts2_diff DECIMAL,
ADD
    COLUMN car_lts3_diff DECIMAL,
ADD
    COLUMN car_lts4_diff DECIMAL;

UPDATE
    reach.hex_reach
SET
    car_lts1_diff = car_len - lts1_len,
    car_lts2_diff = car_len - lts2_len,
    car_lts3_diff = car_len - lts3_len,
    car_lts4_diff = car_len - lts4_len;

-- **** COMPUTE PCT DECREASE IN REACH FROM CAR TO LTS 4 etc. ****
UPDATE
    reach.hex_reach
SET
    lts1_len = 0
WHERE
    lts1_len IS NULL;

UPDATE
    reach.hex_reach
SET
    lts2_len = 0
WHERE
    lts2_len IS NULL;

UPDATE
    reach.hex_reach
SET
    lts3_len = 0
WHERE
    lts3_len IS NULL;

UPDATE
    reach.hex_reach
SET
    lts4_len = 0
WHERE
    lts4_len IS NULL;

UPDATE
    reach.hex_reach
SET
    car_len = 0
WHERE
    car_len IS NULL;

ALTER TABLE
    reach.hex_reach
ADD
    COLUMN car_lts1_diff_pct DECIMAL,
ADD
    COLUMN car_lts2_diff_pct DECIMAL,
ADD
    COLUMN car_lts3_diff_pct DECIMAL,
ADD
    COLUMN car_lts4_diff_pct DECIMAL;

UPDATE
    reach.hex_reach
SET
    car_lts1_diff_pct = (lts1_len / car_len) * 100,
    car_lts2_diff_pct = (lts2_len / car_len) * 100,
    car_lts3_diff_pct = (lts3_len / car_len) * 100,
    car_lts4_diff_pct = (lts4_len / car_len) * 100
WHERE
    car_len > 0;

UPDATE
    reach.hex_reach
SET
    car_lts1_diff_pct = 100
WHERE
    car_len = 0
    AND lts1_len > 0;

UPDATE
    reach.hex_reach
SET
    car_lts2_diff_pct = 100
WHERE
    car_len = 0
    AND lts2_len > 0;

UPDATE
    reach.hex_reach
SET
    car_lts3_diff_pct = 100
WHERE
    car_len = 0
    AND lts3_len > 0;

UPDATE
    reach.hex_reach
SET
    car_lts4_diff_pct = 100
WHERE
    car_len = 0
    AND lts4_len > 0;

-- DROP TABLE IF EXISTS reach.hex_lts_1;
-- DROP TABLE IF EXISTS reach.hex_lts_2;
-- DROP TABLE IF EXISTS reach.hex_lts_3;
-- DROP TABLE IF EXISTS reach.hex_lts_4;
-- DROP TABLE IF EXISTS reach.hex_car;