DROP TABLE IF EXISTS reach.joined,
reach.joined2,
reach.socio_reach_comparison;

CREATE INDEX IF NOT EXISTS hex_reach_component_geom_ix ON reach.compare_reach USING GIST (geometry);

CREATE TABLE reach.joined AS (
    SELECT
        cr. *,
        s.id,
        s.geometry AS socio_geom
    FROM
        reach.compare_reach cr
        JOIN socio s ON ST_Intersects(s.geometry, ST_Centroid(cr.geometry))
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
    cr. *,
    s.id,
    s.geometry AS socio_geom
FROM
    reach.compare_reach cr
    JOIN unjoined s ON ST_Intersects(s.geometry, cr.geometry);

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