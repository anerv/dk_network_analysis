ALTER TABLE
    clustering.hex_clusters
ADD
    column IF NOT EXISTS population FLOAT,
ADD
    COLUMN IF NOT EXISTS population_density FLOAT,
ADD
    COLUMN IF NOT EXISTS urban_pct FLOAT;

UPDATE
    clustering.hex_clusters hc
SET
    population = hg.population,
    population_density = hg.population_density,
    urban_pct = hg.urban_pct
FROM
    hex_grid hg
WHERE
    hc.hex_id = hg.hex_id;