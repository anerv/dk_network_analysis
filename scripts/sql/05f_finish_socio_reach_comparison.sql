ALTER TABLE
    reach.socio_reach_comparison
ADD
    COLUMN IF NOT EXISTS geometry geometry;

UPDATE
    reach.socio_reach_comparison
SET
    geometry = s.geometry
FROM
    socio s
WHERE
    reach.socio_reach_comparison.id = s.id;

DROP TABLE IF EXISTS reach.joined,
reach.joined2;