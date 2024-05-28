ALTER TABLE
    socio
ADD
    COLUMN IF NOT EXISTS households_1car_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_2cars_share DECIMAL,
ADD
    COLUMN IF NOT EXISTS households_nocar_share DECIMAL,
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
    COLUMN IF NOT EXISTS households_with_car INT,
ADD
    COLUMN IF NOT EXISTS households_with_car_share DECIMAL;

UPDATE
    socio
SET
    households_1car_share = households_with_1_car / households,
    households_2cars_share = households_with_2_cars / households,
    households_nocar_share = households_without_car / households,
    households_income_under_100k_share = households_income_under_100k / households,
    households_income_100_150k_share = households_income_100k_150k / households,
    households_income_150_200k_share = households_income_150k_200k / households,
    households_income_200_300k_share = households_income_200k_300k / households,
    households_income_300_400k_share = households_income_300k_400k / households,
    households_income_400_500k_share = households_income_400k_500k / households,
    households_income_500_750k_share = households_income_500k_750k / households,
    households_with_car = households_with_1_car + households_with_2_cars,
    households_with_car_share = (households_with_1_car + households_with_2_cars) / households;