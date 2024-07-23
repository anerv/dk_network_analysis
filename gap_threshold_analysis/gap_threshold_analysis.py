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
    "CREATE TABLE gap_threshold_analysis.edges AS SELECT * FROM gap_threshold_analysis.edges;",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")
print("Created schema!")


result = dbf.run_query_pg("gap_initial_components.sql", connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

print("Created initial components!")

result = dbf.run_query_pg("prepare_gap_data.sql", connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

print("Prepared gap data!")
# %%
# Make columns with different thresholds

thresholds = [10, 20, 30, 40, 50]
thresholds_km = [0.01, 0.02, 0.03, 0.04, 0.05]

lts_values = [1, 2, 3, 4]

#%%

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

    print("Added new columns and dropped tables for threshold", t)

# %%
for i, t in enumerate(thresholds):

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

    print("Created gaps tables for threshold", t)

# %%
for i, t in enumerate(thresholds):
    for lts in lts_values:

        create_index = f"CREATE INDEX IF NOT EXISTS lts{lts}_gap_{t}_geom_ix ON gap_threshold_analysis.lts_{lts}_gaps_{t} USING GIST (geometry);"

        result = dbf.run_query_pg(create_index, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print(f"Created indexes for {t}")

# %%
for i, t in enumerate(thresholds):
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
                INNER JOIN gap_threshold_analysis.lts_{lts}_gaps_{t} l ON ST_Intersects(l.geometry, m.geometry)
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

    print("Deleted unnecessary gaps for threshold", t)

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

    print("Updated gap_threshold_analysis.edges table for threshold", t)

# %%

lts_values_str = ["all", "1", "1_2", "1_3", "1_4"]

for t in thresholds:

    drop_cols = f"""ALTER TABLE
        gap_threshold_analysis.edges DROP COLUMN IF EXISTS component_all_{t},
        DROP COLUMN IF EXISTS component_1_{t},
        DROP COLUMN IF EXISTS component_1_2_{t},
        DROP COLUMN IF EXISTS component_1_3_{t},
        DROP COLUMN IF EXISTS component_1_4_{t},
        DROP COLUMN IF EXISTS component_car_{t};"""

    add_cols = f"""ALTER TABLE
        gap_threshold_analysis.edges
    ADD
        COLUMN IF NOT EXISTS component_all_{t} BIGINT DEFAULT NULL,
    ADD
        COLUMN IF NOT EXISTS component_1_{t} BIGINT DEFAULT NULL,
    ADD
        COLUMN IF NOT EXISTS component_1_2_{t} BIGINT DEFAULT NULL,
    ADD
        COLUMN IF NOT EXISTS component_1_3_{t} BIGINT DEFAULT NULL,
    ADD
        COLUMN IF NOT EXISTS component_1_4_{t} BIGINT DEFAULT NULL;"""

    for q in [drop_cols, add_cols]:
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    for lts_str in lts_values_str:
        drop = f"DROP TABLE IF EXISTS gap_threshold_analysis.components_{lts_str}_{t};"

        result = dbf.run_query_pg(drop, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    create_all = f"""CREATE TABLE gap_threshold_analysis.components_all_{t} AS
    SELECT
        *
    FROM
        pgr_connectedComponents(
            'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges 
            WHERE lts_access IN (1,2,3,4,7) 
            OR lts_1_gap_{t} IS TRUE 
            OR lts_2_gap_{t} IS TRUE 
            OR lts_3_gap_{t} IS TRUE 
            OR lts_4_gap_{t} IS TRUE'
        );"""

    create_1 = f"""CREATE TABLE gap_threshold_analysis.components_1_{t} AS
    SELECT
        *
    FROM
        pgr_connectedComponents(
            'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges 
            WHERE lts_access = 1 OR lts_1_gap_{t} IS TRUE'
        );"""

    create_2 = f"""CREATE TABLE gap_threshold_analysis.components_2_{t} AS
    SELECT
        *
    FROM
        pgr_connectedComponents(
            'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges
            WHERE lts_access IN (1,2) OR lts_1_gap_{t} IS TRUE or lts_2_gap_{t} IS TRUE'
        );"""

    create_3 = f"""CREATE TABLE gap_threshold_analysis.components_3_{t} AS
    SELECT
        *
    FROM
        pgr_connectedComponents(
            'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges
          WHERE lts_access IN (1,2,3) OR lts_1_gap_{t} IS TRUE OR lts_2_gap_{t} IS TRUE 
          OR lts_3_gap_{t} IS TRUE'
        );"""

    create_4 = f"""CREATE TABLE gap_threshold_analysis.components_4_{t} AS
    SELECT
        *
    FROM
        pgr_connectedComponents(
            'SELECT id, source, target, cost, reverse_cost FROM gap_threshold_analysis.edges
          WHERE lts_access IN (1,2,3,4) OR lts_1_gap_{t} IS TRUE or lts_2_gap_{t} IS TRUE 
          OR lts_3_gap_{t} IS TRUE OR lts_4_gap_{t} IS TRUE'
        );"""

    for c in [create_all, create_1, create_2, create_3, create_4]:
        result = dbf.run_query_pg(c, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print("Created components tables for threshold", t)

# %%

for t in thresholds:

    update_all = f"""UPDATE
        gap_threshold_analysis.edges e
    SET
        component_all_{t} = component
    FROM
        gap_threshold_analysis.components_all_{t} co
    WHERE
        e.source = co.node
        AND (
            lts_access IN (1, 2, 3, 4, 7)
            OR lts_1_gap_{t} IS TRUE
            OR lts_2_gap_{t} IS TRUE
            OR lts_3_gap_{t} IS TRUE
            OR lts_4_gap_{t} IS TRUE
        );"""

    update_1 = f"""UPDATE
        gap_threshold_analysis.edges e
    SET
        component_1_{t} = component
    FROM
        gap_threshold_analysis.components_1_{t} co
    WHERE
        e.source = co.node
        AND (
            lts_access = 1
            OR lts_1_gap_{t} IS TRUE
        );"""

    update_2 = f"""UPDATE
        gap_threshold_analysis.edges e
    SET
        component_1_2 = component
    FROM
        gap_threshold_analysis.components_2_{t} co
    WHERE
        e.source = co.node
        AND (
            lts_access IN (1, 2)
            OR lts_1_gap_{t} IS TRUE
            OR lts_2_gap_{t} IS TRUE
        );"""

    update_3 = f"""UPDATE
        gap_threshold_analysis.edges e
    SET
        component_1_3 = component
    FROM
        gap_threshold_analysis.components_3_{t} co
    WHERE
        e.source = co.node
        AND (
            lts_access IN (1, 2, 3)
            OR lts_1_gap_{t} IS TRUE
            OR lts_2_gap_{t} IS TRUE
            OR lts_3_gap_{t} IS TRUE
        );"""

    update_4 = f"""UPDATE
        gap_threshold_analysis.edges e
    SET
        component_1_4 = component
    FROM
        gap_threshold_analysis.components_4_{t} co
    WHERE
        e.source = co.node
        AND (
            lts_access IN (1, 2, 3, 4)
            OR lts_1_gap_{t} IS TRUE
            OR lts_2_gap_{t} IS TRUE
            OR lts_3_gap_{t} IS TRUE
            OR lts_4_gap_{t} IS TRUE
        );"""

    for u in [update_all, update_1, update_2, update_3, update_4]:
        result = dbf.run_query_pg(u, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    print("Updated edge components for threshold", t)

# %%

lts_list = []
threshold_values = []
gap_count = []

for t in thresholds:

    threshold_values.extend([t]*(len(lts_values)))
    lts_list.extend(lts_values)

    for lts in lts_values:
        gaps = gpd.read_postgis(
            f"SELECT * FROM gap_threshold_analysis.edges WHERE lts_{lts}_gap_{t} IS TRUE",
            engine,
            geom_col="geometry",
        )

        gap_count.append(len(gaps))
        print(f"Number of gaps for lts {lts} and threshold {t}: {len(gaps)}")


assert len(lts_list) == len(gap_count) == len(threshold_values)

gap_df = pd.DataFrame(data={"lts": lts_list, "threshold": threshold_values, "gap_count": gap_count})


# Group the data by threshold and lts
grouped_data = gap_df.groupby(['threshold', 'lts']).sum().reset_index()

# Pivot the data to create a matrix for stacked bar chart
pivot_data = grouped_data.pivot(index='threshold', columns='lts', values='gap_count')

colors = list(lts_color_dict.values())

# Plot the stacked bar chart
pivot_data.plot(kind='bar', stacked=True, color=colors)

# Set the labels and title
plt.xlabel('Threshold (m)')
plt.ylabel('Number of identified gaps')
plt.title('Number of gaps by threshold and LTS')

# Move the legend to the right of the plot
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

# Show the plot
plt.show()
# %%

lts_list = []
threshold_values = []
component_counts = []

for t in thresholds:

    threshold_values.extend([t]*(len(lts_values)))
    lts_list.extend(lts_values)

    for lts in lts_values:

        components = pd.read_sql(
            f"SELECT COUNT(DISTINCT component) FROM gap_threshold_analysis.components_{lts}_{t}",
            engine,
        )

        component_counts.append(components.loc[0,"count"])

        print(f"Number of components for lts {lts} and threshold {t}: {components.loc[0,"count"]:,}")


assert len(lts_list) == len(component_counts) == len(threshold_values)

threshold_df = pd.DataFrame(data={"lts": lts_list, "threshold": threshold_values, "component_count": component_counts})


# Group the data by threshold and lts
grouped_data = threshold_df.groupby(['threshold', 'lts']).sum().reset_index()

# Pivot the data to create a matrix for stacked bar chart
pivot_data = grouped_data.pivot(index='threshold', columns='lts', values='component_count')


# Plot the stacked bar chart
colors = list(lts_color_dict.values())
pivot_data.plot(kind='bar', stacked=True, color=colors)

# Set the labels and title
plt.xlabel('Threshold (m)')
plt.ylabel('Number of components')
plt.title('Number of components by threshold and LTS')

# Move the legend to the right of the plot
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

# Show the plot
plt.show()

connection.close()
# %%
