ALTER TABLE
    edges
ADD
    COLUMN IF NOT EXISTS lts_access INT DEFAULT NULL;

UPDATE
    edges e
SET
    lts_access = CASE
        WHEN lts_viz = 'all_cyclists' THEN 1
        WHEN lts_viz = 'most_cyclists' THEN 2
        WHEN lts_viz = 'confident_cyclists' THEN 3
        WHEN lts_viz = 'very_confident_cyclists' THEN 4
        WHEN lts_viz = 'paths_bike' THEN 5
        WHEN lts_viz = 'pedestrian' THEN 6
        WHEN lts_viz = 'no_cycling' THEN 7
        WHEN lts_viz = 'no_access' THEN 0
        WHEN lts_viz = 'dirt_road' THEN 8
        ELSE NULL
    END;

DO $$
DECLARE
    lts_missing INT;

BEGIN
    SELECT
        COUNT(*) INTO lts_missing
    FROM
        edges
    WHERE
        lts_access IS NULL;

ASSERT lts_missing = 0,
'Edges missing LTS value';

END $$;