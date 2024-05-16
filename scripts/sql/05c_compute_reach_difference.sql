-- ***** JOIN REACH TO ORIGINAL HEX GEOMETRIES *****
CREATE INDEX IF NOT EXISTS h3_grid_ix ON h3_grid (hex_id);

CREATE INDEX IF NOT EXISTS lts_1_reach_ix ON lts_1_reach (hex_id);

CREATE INDEX IF NOT EXISTS lts_2_reach_ix ON lts_2_reach (hex_id);

CREATE INDEX IF NOT EXISTS lts_3_reach_ix ON lts_3_reach (hex_id);

CREATE INDEX IF NOT EXISTS lts_4_reach_ix ON lts_4_reach (hex_id);

CREATE INDEX IF NOT EXISTS car_reach_ix ON car_reach (hex_id);

CREATE TABLE reach.hex_reach AS
SELECT
    h.hex_id,
    h.geometry,
    l1.edge_length AS l1_len,
    l1.coverage_area AS l1_area,
    l2.edge_length AS l2_len,
    l2.coverage_area AS l2_area,
    l3.edge_length AS l3_len,
    l3.coverage_area AS l3_area,
    l4.edge_length AS l4_len,
    l4.coverage_area AS l4_area,
    ca.edge_length AS car_len,
    ca.coverage_area AS car_area
FROM
    h3_grid h
    LEFT JOIN lts_1_reach l1 ON h.hex_id = l1.hex_id
    LEFT JOIN lts_2_reach l2 ON h.hex_id = l2.hex_id
    LEFT JOIN lts_3_reach l3 ON h.hex_id = l3.hex_id
    LEFT JOIN lts_4_reach l4 ON h.hex_id = l4.hex_id
    LEFT JOIN car_reach ca ON h.hex_id = ca.hex_id;

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
    adm_boundaries.geometry
FROM
    adm_boundaries
    LEFT JOIN lts_1 ON adm_boundaries.navn = lts_1.municipality
    LEFT JOIN lts_2 ON adm_boundaries.navn = lts_2.municipality
    LEFT JOIN lts_3 ON adm_boundaries.navn = lts_3.municipality
    LEFT JOIN lts_4 ON adm_boundaries.navn = lts_4.municipality
    LEFT JOIN lts_5 ON adm_boundaries.navn = lts_5.municipality
    LEFT JOIN lts_6 ON adm_boundaries.navn = lts_6.municipality
    LEFT JOIN lts_7 ON adm_boundaries.navn = lts_7.municipality
    LEFT JOIN total_car ON adm_boundaries.navn = total_car.municipality;

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
    h3_grid;

ASSERT hex_grid_len = hex_reach_len,
'Missing hex cells!';

END $$;

-- **** COMPUTE PCT DECREASE IN REACH FROM CAR TO LTS 4 etc. ****
ALTER TABLE
    reach.hex_reach
ADD
    COLUMN pct_lts_1_len DECIMAL,
ADD
    COLUMN pct_lts_2_len DECIMAL,
ADD
    COLUMN pct_lts_3_len DECIMAL,
ADD
    COLUMN pct_lts_4_len DECIMAL,
ADD
    COLUMN pct_lts_1_cover DECIMAL,
ADD
    COLUMN pct_lts_2_cover DECIMAL,
ADD
    COLUMN pct_lts_3_cover DECIMAL,
ADD
    COLUMN pct_lts_4_cover DECIMAL;

UPDATE
    reach.hex_reach
SET
    pct_lts_1_len = (l1_len / car_len) * 100,
    pct_lts_2_len = (l2_len / car_len) * 100,
    pct_lts_3_len = (l3_len / car_len) * 100,
    pct_lts_4_len = (l4_len / car_len) * 100;

UPDATE
    reach.hex_reach
SET
    pct_lts_1_cover = (l1_area / car_area) * 100,
    pct_lts_2_cover = (l2_area / car_area) * 100,
    pct_lts_3_cover = (l3_area / car_area) * 100,
    pct_lts_4_cover = (l4_area / car_area) * 100;

DROP TABLE IF EXISTS reach.hex_lts_1;

DROP TABLE IF EXISTS reach.hex_lts_2;

DROP TABLE IF EXISTS reach.hex_lts_3;

DROP TABLE IF EXISTS reach.hex_lts_4;

DROP TABLE IF EXISTS reach.hex_car;