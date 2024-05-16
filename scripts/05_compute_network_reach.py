# %%

from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import math
import matplotlib.pyplot as plt


exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

# %%
engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%
queries = [
    "sql/05a_prepare_reach_computation.sql",
    "sql/05b_create_hexagon_centroids.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")


# %%
# **** COMPUT REACHABLE NODES ****
table_names = [
    "reach.lts_1_reach",
    "reach.lts_2_reach",
    "reach.lts_3_reach",
    "reach.lts_4_reach",
    "reach.car_reach",
]

edge_tables = ["lts_1_edges", "lts_2_edges", "lts_3_edges", "lts_4_edges", "car_edges"]

hex_tables = [
    "reach.hex_lts_1",
    "reach.hex_lts_2",
    "reach.hex_lts_3",
    "reach.hex_lts_4",
    "reach.hex_car",
]

dist = 5  # max distance in km

# CREATE TABLES
for t in table_names:

    q = f"DROP TABLE IF EXISTS {t};"

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    q = f"""CREATE TABLE {t} (
        start_node INTEGER DEFAULT NULL,
        reachable_nodes VARCHAR DEFAULT NULL
    );"""

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break


# %%
# COMPUTE REACHABLE NODES USING CHUNKS

for i, t in enumerate(table_names):

    print(f"At round: {i}")

    # GET ALL IDS
    df = pd.read_sql_query(f"SELECT node_id FROM {hex_tables[i]}", con=engine)
    node_ids = df.node_id.to_list()

    for ids_chunk in dbf.get_chunks(sequence=node_ids, chunk_size=1000):

        # for ids in ids_chunk:

        q = f"""
        INSERT INTO
            {t} (
                SELECT
                    from_v AS start_node,
                    ARRAY_AGG(
                        node
                        ORDER BY
                            node
                    ) AS reachable_nodes
                FROM
                    pgr_drivingDistance(
                        'SELECT id, source, target, km AS cost FROM {edge_tables[i]}',
                        (
                           array{ids_chunk}
                                
                        )
                        ,
                        {dist},
                        FALSE
                    )
                GROUP BY
                    from_v
            );"""

        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break


# %%

# **** COMPUT REACHABLE EDGES ****

# Add new columns
table_names = [
    "reach.lts_1_reach",
    "reach.lts_2_reach",
    "reach.lts_3_reach",
    "reach.lts_4_reach",
    "reach.car_reach",
]

edge_tables = ["lts_1_edges", "lts_2_edges", "lts_3_edges", "lts_4_edges", "car_edges"]

hex_tables = [
    "reach.hex_lts_1",
    "reach.hex_lts_2",
    "reach.hex_lts_3",
    "reach.hex_lts_4",
    "reach.hex_car",
]

for t in table_names:

    q = f"""
        ALTER TABLE
            {t}
        ADD
            COLUMN IF NOT EXISTS reached_edges VARCHAR DEFAULT NULL,
        ADD
            COLUMN IF NOT EXISTS edge_length NUMERIC DEFAULT NULL,
        ADD
            COLUMN IF NOT EXISTS convex_hull GEOMETRY,
        ADD
            COLUMN IF NOT EXISTS coverage_area NUMERIC DEFAULT NULL;
        """

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

# %%
for i, t in enumerate(table_names):

    print(f"At round: {i}")

    # TODO: use start_nodes to get subsets??
    # GET ALL IDS
    df = pd.read_sql_query(f"SELECT node_id FROM {hex_tables[i]}", con=engine)
    node_ids = tuple(df.node_id.to_list())

    for ids_chunk in dbf.get_chunks(sequence=node_ids, chunk_size=1000):

        q = f"""WITH joined_edges AS (
            SELECT
                start_node,
                array_agg(e.id) AS reachable_edges,
                SUM(ST_Length(e.geometry)) AS total_length
            FROM
                {t}
                JOIN {edge_tables[i]} e ON e.source = ANY({t}.reachable_nodes::int[])
                AND e.target = ANY({t}.reachable_nodes::int[]) 
            WHERE 
                start_node IN {ids_chunk}
            GROUP BY
                start_node 
        )
        UPDATE
            {t}
        SET
            reached_edges = j.reachable_edges,
            edge_length = j.total_length
        FROM
            joined_edges j
        WHERE
            {t}.start_node = j.start_node;"""

        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break
# %%
for i, t in enumerate(table_names[0:1]):

    # TODO: use start_nodes to get subsets??
    # GET ALL IDS
    df = pd.read_sql_query(f"SELECT node_id FROM {hex_tables[i]}", con=engine)
    node_ids = tuple(df.node_id.to_list())

    for ids_chunk in dbf.get_chunks(sequence=node_ids, chunk_size=1000):

        q = f"""WITH joined_nodes AS (
            SELECT
                start_node,
                ST_ConcaveHull(ST_Collect(n.geometry), 0.4, FALSE) AS geometry
            FROM
                {t}
                JOIN nodes n ON n.id = ANY({t}.reachable_nodes::int[])
            GROUP BY
                start_node WHERE start_node IN {ids_chunk}
        )
        UPDATE
            {t}
        SET
            convex_hull = j.geometry,
            coverage_area = ST_Area(j.geometry)
        FROM
            joined_nodes j
        WHERE
            {t}.start_node = j.start_node;"""

        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break
# %%
connection.close()

with open("vacuum_analyze.py") as f:
    exec(f.read())

print("Script 05 complete!")
