ALTER TABLE
    socio
ADD
    COLUMN IF NOT EXISTS households_1car_pct DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_2cars_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_nocar_pct DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_under_100k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_100_150k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_150_200k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_200_300k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_300_400k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_400_500k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_500_750k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_income_750k_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_with_car INT,
ADD
    COLUMN IF NOT EXISTS households_with_car_pct DECIMAL;

UPDATE
    socio
SET
    households_1car_pct = households_with_1_car / households,
    households_2cars_share = households_with_2_cars / households,
    households_nocar_pct = households_without_car / households,
    households_income_under_100k_share = households_income_under_100k / households,
    households_income_100_150k_share = households_income_100k_150k / households,
    households_income_150_200k_share = households_income_150k_200k / households,
    households_income_200_300k_share = households_income_200k_300k / households,
    households_income_300_400k_share = households_income_300k_400k / households,
    households_income_400_500k_share = households_income_400k_500k / households,
    households_income_500_750k_share = households_income_500k_750k / households,
    households_income_750k_share = households_income_750k_ / households,
    households_with_car = households_with_1_car + households_with_2_cars,
    households_with_car_pct = (households_with_1_car + households_with_2_cars) / households;

ALTER TABLE
    socio
ADD
    COLUMN IF NOT EXISTS urban_pct DECIMAL;

WITH inter AS (
    SELECT
        so.id AS id,
        SUM(
            ST_Area(ST_Intersection(so.geometry, ub.geometry))
        ) AS intersection_area
    FROM
        socio AS so,
        urban_areas AS ub
    WHERE
        ST_Intersects(so.geometry, ub.geometry)
    GROUP BY
        so.id
)
UPDATE
    socio
SET
    urban_pct = (
        inter.intersection_area / ST_Area(socio.geometry)
    ) * 100
FROM
    inter
WHERE
    socio.id = inter.id;

UPDATE
    socio
SET
    urban_pct = 0
WHERE
    urban_pct IS NULL;