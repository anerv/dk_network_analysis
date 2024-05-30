CREATE TABLE reach.compare_reach AS (
    SELECT
        r5.hex_id,
        r5.lts1_reach AS lts1_reach_5,
        r5.lts2_reach AS lts2_reach_5,
        r5.lts3_reach AS lts3_reach_5,
        r5.lts4_reach AS lts4_reach_5,
        r5.car_reach AS car_reach_5,
        r10.lts1_reach AS lts1_reach_10,
        r10.lts2_reach AS lts2_reach_10,
        r10.lts3_reach AS lts3_reach_10,
        r10.lts4_reach AS lts4_reach_10,
        r10.car_reach AS car_reach_10,
        r15.lts1_reach AS lts1_reach_15,
        r15.lts2_reach AS lts2_reach_15,
        r15.lts3_reach AS lts3_reach_15,
        r15.lts4_reach AS lts4_reach_15,
        r15.car_reach AS car_reach_15
    FROM
        reach.reach.hex_reach_5 r5
        LEFT JOIN reach.reach.hex_reach_10 r10 ON r5.hex_id = r10.hex_id
        LEFT JOIN reach.reach.hex_reach_15 r15 ON r5.hex_id = r15.hex_id
);

-- CREATE TABLE reach.centroids AS
-- SELECT
--     ST_Centroid(geometry) AS geometry,
--     hex_id
-- FROM
--     hex_grid;
-- CREATE INDEX IF NOT EXISTS centroid_geom_ix ON reach.centroids USING GIST (geometry);
CREATE INDEX IF NOT EXISTS hex_reach_5_geom_ix ON reach.hex_reach_5 USING GIST (geometry);

CREATE TABLE socio_ave_reach AS
SELECT
    s.id,
    AVE(r.lts1_reach) AS lts1_reach_average,
    AVE(r.lts2_reach) AS lts2_reach_average,
    AVE(r.lts3_reach) AS lts3_reach_average,
    AVE(r.lts4_reach) AS lts4_reach_average,
    AVE(r.car_reach) AS car_reach_average,
    MIN(r.lts1_reach) AS lts1_reach_min,
    MIN(r.lts2_reach) AS lts2_reach_min,
    MIN(r.lts3_reach) AS lts3_reach_min,
    MIN(r.lts4_reach) AS lts4_reach_min,
    MIN(r.car_reach) AS car_reach_min,
    MAX(r.lts1_reach) AS lts1_reach_max,
    MAX(r.lts2_reach) AS lts2_reach_max,
    MAX(r.lts3_reach) AS lts3_reach_max,
    MAX(r.lts4_reach) AS lts4_reach_max,
    MAX(r.car_reach) AS car_reach_max,
    MEDIAN(r.lts1_reach) AS lts1_reach_median,
    MEDIAN(r.lts2_reach) AS lts2_reach_median,
    MEDIAN(r.lts3_reach) AS lts3_reach_median,
    MEDIAN(r.lts4_reach) AS lts4_reach_median,
    MEDIAN(r.car_reach) AS car_reach_median
FROM
    socio s
    LEFT JOIN reach.hex_reach_5 r ON ST_Intersects(s.geometry, ST_Centroid(r.geometry));

-- ALTERNATIVELY - JOIN socio to hex_reach, group by socio id, compute ave, min, max, median, join with socio geoms