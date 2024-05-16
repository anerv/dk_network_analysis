DROP TABLE IF EXISTS andreas_export;

DROP TABLE IF EXISTS andreas_export_nodes;

CREATE TABLE andreas_export AS (
    SELECT
        *
    FROM
        edges
    WHERE
        municipality IN (
            -- 'Albertslund',
            -- 'Allerød',
            -- 'Ballerup',
            -- 'Brøndby',
            -- 'Dragør',
            -- 'Egedal',
            -- 'Fredensborg',
            'Frederiksberg',
            -- 'Frederikssund',
            -- 'Furesø',
            -- 'Gentofte',
            -- 'Gladsaxe',
            -- 'Glostrup',
            -- 'Greve',
            -- 'Gribskov',
            -- 'Halsnæs',
            -- 'Helsingør',
            -- 'Herlev',
            -- 'Hillerød',
            -- 'Hvidovre',
            -- 'Høje-Taastrup',
            -- 'Hørsholm',
            -- 'Ishøj',
            'København',
            -- 'Køge',
            -- 'Lyngby-Taarbæk',
            -- 'Roskilde',
            -- 'Rudersdal',
            -- 'Rødovre',
            -- 'Solrød',
            -- 'Tårnby',
            -- 'Vallensbæk'
        )
);

CREATE TABLE andreas_export_nodes AS (
    SELECT
        *
    FROM
        nodes
    WHERE
        id IN (
            SELECT
                source AS node
            FROM
                andreas_export
            UNION
            SELECT
                target AS node
            FROM
                andreas_export
        )
);