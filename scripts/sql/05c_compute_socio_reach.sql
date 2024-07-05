DROP TABLE IF EXISTS reach.joined,
reach.joined2,
reach.socio_reach_5;

CREATE INDEX IF NOT EXISTS hex_reach_5_geom_ix ON reach.hex_reach_5 USING GIST (geometry);

CREATE TABLE reach.joined AS (
    SELECT
        r5. *,
        s.id,
        s.geometry AS socio_geom
    FROM
        reach.hex_reach_5 r5
        JOIN socio s ON ST_Intersects(s.geometry, ST_Centroid(r5.geometry))
);

CREATE TABLE reach.joined2 AS WITH unjoined AS (
    SELECT
        *
    FROM
        socio
    WHERE
        id NOT IN (
            SELECT
                DISTINCT id
            FROM
                reach.joined
        )
)
SELECT
    r5. *,
    s.id,
    s.geometry AS socio_geom
FROM
    reach.hex_reach_5 r5
    JOIN unjoined s ON ST_Intersects(s.geometry, r5.geometry);

INSERT INTO
    reach.joined (
        SELECT
            *
        FROM
            reach.joined2
        WHERE
            id NOT IN (
                SELECT
                    DISTINCT id
                FROM
                    reach.joined
            )
    );

CREATE TABLE reach.socio_reach_5 AS
SELECT
    j.id,
    AVG(j.lts_1_reach) AS lts_1_reach_average,
    AVG(j.lts_1_2_reach) AS lts_1_2_reach_average,
    AVG(j.lts_1_3_reach) AS lts_1_3_reach_average,
    AVG(j.lts_1_4_reach) AS lts_1_4_reach_average,
    AVG(j.car_reach) AS car_reach_average,
    MIN(j.lts_1_reach) AS lts_1_reach_min,
    MIN(j.lts_1_2_reach) AS lts_1_2_reach_min,
    MIN(j.lts_1_3_reach) AS lts_1_3_reach_min,
    MIN(j.lts_1_4_reach) AS lts_1_4_reach_min,
    MIN(j.car_reach) AS car_reach_min,
    MAX(j.lts_1_reach) AS lts_1_reach_max,
    MAX(j.lts_1_2_reach) AS lts_1_2_reach_max,
    MAX(j.lts_1_3_reach) AS lts_1_3_reach_max,
    MAX(j.lts_1_4_reach) AS lts_1_4_reach_max,
    MAX(j.car_reach) AS car_reach_max,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.lts_1_reach
    ) AS lts_1_reach_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.lts_1_2_reach
    ) AS lts_1_2_reach_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.lts_1_3_reach
    ) AS lts_1_3_reach_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.lts_1_4_reach
    ) AS lts_1_4_reach_median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            j.car_reach
    ) AS car_reach_median
FROM
    reach.joined j
GROUP BY
    j.id;

ALTER TABLE
    reach.socio_reach_5
ADD
    COLUMN IF NOT EXISTS geometry geometry;

UPDATE
    reach.socio_reach_5
SET
    geometry = s.geometry
FROM
    socio s
WHERE
    reach.socio_reach_5.id = s.id;

DROP TABLE IF EXISTS reach.joined,
reach.joined2;