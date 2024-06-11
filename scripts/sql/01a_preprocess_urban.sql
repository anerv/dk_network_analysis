DROP TABLE IF EXISTS urban_areas_dissolved;

CREATE TABLE urban_areas_dissolved AS
SELECT
    (ST_Dump(geometry)) .geom AS geometry
FROM
    (
        SELECT
            ST_Union(geometry) AS geometry
        FROM
            urban_areas
    ) sq;

DROP TABLE IF EXISTS urban_areas;

ALTER TABLE
    urban_areas_dissolved RENAME TO urban_areas;

CREATE INDEX IF NOT EXISTS urban_geom_ix ON urban_areas USING GIST (geometry);