CREATE INDEX IF NOT EXISTS id_ix ON edges (id);

CREATE INDEX IF NOT EXISTS lts_ix ON edges (lts);

CREATE INDEX IF NOT EXISTS source_ix ON edges (source);

CREATE INDEX IF NOT EXISTS target_ix ON edges (target);

CREATE INDEX IF NOT EXISTS edges_geom_ix ON edges USING GIST (geometry);