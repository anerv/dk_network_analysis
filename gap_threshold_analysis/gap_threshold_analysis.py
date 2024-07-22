# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

# %%

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%

queries = [
    "DROP SCHEMA IF EXISTS gap_threshold_analysis CASCADE;",
    "CREATE SCHEMA gap_threshold_analysis;",
    "CREATE TABLE gap_threshold_analysis.edges AS SELECT * FROM edges;",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")
print("Created schema!")

# %%

result = dbf.run_query_pg("gap_initial_components.sql", connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

print("Created initial components!")

# %%
result = dbf.run_query_pg("prepare_gap_data.sql", connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

print("Prepared gap data!")
# %%
# Make columns with different thresholds

thresholds = [10, 20, 30, 40, 50]
thresholds_km = [0.01, 0.02, 0.03, 0.04, 0.05]

lts_values = [1, 2, 3, 4]

for i, t in enumerate(thresholds):

    add_cols = f"""ALTER TABLE
        gap_threshold_analysis.edges
    ADD
        COLUMN IF NOT EXISTS lts_1_gap_{t} BOOLEAN,
    ADD
        COLUMN IF NOT EXISTS lts_2_gap_{t} BOOLEAN,
    ADD
        COLUMN IF NOT EXISTS lts_3_gap_{t} BOOLEAN,
    ADD
        COLUMN IF NOT EXISTS lts_4_gap_{t} BOOLEAN;"""

    result = dbf.run_query_pg(add_cols, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

    for lts in lts_values:

        drop = f"DROP TABLE IF EXISTS gap_threshold_analysis.lts_{lts}_gaps_{t};"

        result = dbf.run_query_pg(drop, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print("Added new columns and dropped tables")

    # -- LTS GAPS 1
    create_gaps_1 = f"""CREATE TABLE gap_threshold_analysis.lts_1_gaps_{t} AS
    SELECT
        e.name,
        e.municipality,
        e.id,
        e.lts,
        e.lts_access,
        e.all_access,
        e.cycling_allowed,
        e.source,
        e.target,
        e.bicycle,
        e.highway,
        e.geometry
    FROM
        gap_threshold_analysis.edges AS e
        JOIN gap_threshold_analysis.nodes_lts_1 AS ns ON e.source = ns.node
        JOIN gap_threshold_analysis.nodes_lts_1 AS nt ON e.target = nt.node
        LEFT JOIN gap_threshold_analysis.components_1 AS co1 ON e.source = co1.node
        LEFT JOIN gap_threshold_analysis.components_1 AS co2 ON e.target = co2.node
    WHERE
        e.lts <> 1
        AND e.km <= {thresholds_km[i]}
        AND e.all_access = TRUE
        AND co1.component <> co2.component;"""

    # -- LTS GAPS 2
    create_gaps_2 = f"""CREATE TABLE gap_threshold_analysis.lts_2_gaps_{t} AS
    SELECT
        e.name,
        e.municipality,
        e.id,
        e.lts,
        e.lts_access,
        e.all_access,
        e.cycling_allowed,
        e.source,
        e.target,
        e.bicycle,
        e.highway,
        e.geometry
    FROM
        gap_threshold_analysis.edges AS e
        JOIN gap_threshold_analysis.nodes_lts_2 AS ns ON e.source = ns.node
        JOIN gap_threshold_analysis.nodes_lts_2 AS nt ON e.target = nt.node
        LEFT JOIN gap_threshold_analysis.components_2 AS co1 ON e.source = co1.node
        LEFT JOIN gap_threshold_analysis.components_2 AS co2 ON e.target = co2.node
    WHERE
        e.lts <> 2
        AND e.km <= {thresholds_km[i]}
        AND e.all_access = TRUE
        AND co1.component <> co2.component;"""

    # -- LTS GAPS 3
    create_gaps_3 = f"""CREATE TABLE gap_threshold_analysis.lts_3_gaps_{t} AS
    SELECT
        e.name,
        e.municipality,
        e.id,
        e.lts,
        e.lts_access,
        e.all_access,
        e.cycling_allowed,
        e.source,
        e.target,
        e.bicycle,
        e.highway,
        e.geometry
    FROM
        gap_threshold_analysis.edges AS e
        JOIN gap_threshold_analysis.nodes_lts_3 AS ns ON e.source = ns.node
        JOIN gap_threshold_analysis.nodes_lts_3 AS nt ON e.target = nt.node
        LEFT JOIN gap_threshold_analysis.components_3 AS co1 ON e.source = co1.node
        LEFT JOIN gap_threshold_analysis.components_3 AS co2 ON e.target = co2.node
    WHERE
        e.lts <> 3
        AND e.km <= {thresholds_km[i]}
        AND e.all_access = TRUE
        AND co1.component <> co2.component;"""

    # -- LTS GAPS 4
    create_gaps_4 = f"""CREATE TABLE gap_threshold_analysis.lts_4_gaps_{t} AS
    SELECT
        e.name,
        e.municipality,
        e.id,
        e.lts,
        e.lts_access,
        e.all_access,
        e.cycling_allowed,
        e.source,
        e.target,
        e.bicycle,
        e.highway,
        e.geometry
    FROM
        gap_threshold_analysis.edges AS e
        JOIN gap_threshold_analysis.nodes_lts_4 AS ns ON e.source = ns.node
        JOIN gap_threshold_analysis.nodes_lts_4 AS nt ON e.target = nt.node
        LEFT JOIN gap_threshold_analysis.components_4 AS co1 ON e.source = co1.node
        LEFT JOIN gap_threshold_analysis.components_4 AS co2 ON e.target = co2.node
    WHERE
        e.lts <> 4
        AND e.km <= {thresholds_km[i]}
        AND e.all_access = TRUE
        AND co1.component <> co2.component;"""

    create_gaps = [create_gaps_1, create_gaps_2, create_gaps_3, create_gaps_4]
    for c in create_gaps:
        result = dbf.run_query_pg(c, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print("Created gaps tables")

    for lts in lts_values:

        create_index = f"CREATE INDEX IF NOT EXISTS lts{lts}_gap_geom_ix ON gap_threshold_analysis.lts_{lts}_gaps USING GIST (geometry);"

        result = dbf.run_query_pg(create_gaps_1, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print("Created indexes")

    for lts in lts_values:
        # --DROP gaps that form too long stretches
        drop = f"""WITH merged AS (
            SELECT
                (ST_Dump(ST_LineMerge(ST_Collect(geometry)))) .geom AS geometry
            FROM
                gap_threshold_analysis.lts_{lts}_gaps_{t}
        ),
        too_long_gaps AS (
            SELECT
                --row_number() OVER () AS cid,
                l.id --,
                --m.geometry
            FROM
                merged m
                INNER JOIN lts_1_gaps l ON ST_Intersects(l.geometry, m.geometry)
            WHERE
                ST_Length(m.geometry) > 30
        )
        DELETE FROM
            gap_threshold_analysis.lts_{lts}_gaps_{t}
        WHERE
            id IN (
                SELECT
                    id
                FROM
                    too_long_gaps
            );"""

        # -- CONSIDER - close gaps for pedestrian, no cycling, etc?
        delete1 = f"""DELETE FROM
            gap_threshold_analysis.lts_{lts}_gaps_{t}
        WHERE
            lts_access IN (0, 7)
            AND bicycle <> 'use_sidepath';"""

        delete2 = f"""DELETE FROM
           gap_threshold_analysis.lts_{lts}_gaps_{t}
        WHERE
            lts_access IN (0, 7)
            AND bicycle = 'use_sidepath'
            AND highway IN (
                'motorway',
                'motorway_link',
                'trunk',
                'trunk_link'
            );"""

    for q in [drop, delete1, delete2]:
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print("Deleted unnecessary gaps")

    ###-----
    for lts in lts_values:

        update = f"""UPDATE
            gap_threshold_analysis.edges
        SET
            lts_{lts}_gap_{t} = TRUE
        WHERE
            id IN (
                SELECT
                    id
                FROM
                    gap_threshold_analysis.lts_{lts}_gaps_{t}
            );"""

        result = dbf.run_query_pg(update, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print("Updated edges table")
