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
# REACH PARAMETERS
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
buffer_dist = 10  # buffer distance in meters


# %%

# **** COMPUT REACHABLE NODES ****

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
# CREATE INDICES

result = dbf.run_query_pg(
    "CREATE INDEX IF NOT EXISTS idx_nodes_id ON nodes(id);", connection
)

if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

for i, t in enumerate(table_names):

    l = i + 1
    q = f"CREATE INDEX IF NOT EXISTS idx_reach_{l}_start_node ON {t}(start_node);"

    result = dbf.run_query_pg(q, connection)

    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break


# %%
# **** COMPUT REACHABLE EDGES ****

# Add new columns

for t in table_names:

    q = f"""
        ALTER TABLE
            {t}
        ADD
            COLUMN IF NOT EXISTS reachable_edges VARCHAR DEFAULT NULL,
        ADD
            COLUMN IF NOT EXISTS edge_length NUMERIC DEFAULT NULL,
        ADD
            COLUMN IF NOT EXISTS coverage_area NUMERIC DEFAULT NULL;
        """

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

# %%

with open("vacuum_analyze.py") as f:
    exec(f.read())

# %%
# compute reachable edges
for i, t in enumerate(table_names):

    print(f"At round: {i}")

    # GET ALL IDS
    df = pd.read_sql_query(f"SELECT node_id FROM {hex_tables[i]}", con=engine)
    node_ids = tuple(df.node_id.to_list())

    for ids_chunk in dbf.get_chunks(sequence=node_ids, chunk_size=1000):

        q = f"""
            WITH filtered_nodes AS (
                SELECT *
                FROM {t}
                WHERE start_node IN {ids_chunk}
            ),
            filtered_edges AS (
                SELECT e.id, e.source, e.target, e.geometry, ST_Length(e.geometry) AS length
                FROM {edge_tables[i]} e
                WHERE e.source IN (
                    SELECT unnest(reachable_nodes::int[]) FROM filtered_nodes
                ) OR e.target IN (
                    SELECT unnest(reachable_nodes::int[]) FROM filtered_nodes
                )
            ),
            joined_edges AS (
                SELECT
                    fn.start_node,
                    array_agg(fe.id) AS reachable_edges,
                    SUM(fe.length) AS total_length,
                    ST_Union(fe.geometry) AS geometry
                FROM filtered_nodes fn
                JOIN filtered_edges fe
                ON fe.source = ANY(fn.reachable_nodes::int[])
                AND fe.target = ANY(fn.reachable_nodes::int[])
                GROUP BY fn.start_node
            )
            UPDATE {t} rc
            SET
                reachable_edges = j.reachable_edges,
                edge_length = j.total_length,
                coverage_area = ST_Area(ST_Buffer(j.geometry, 10))
            FROM joined_edges j
            WHERE rc.start_node = j.start_node;
        
        """

        # q = f"""WITH joined_edges AS (
        #     SELECT
        #         start_node,
        #         array_agg(e.id) AS reachable_edges,
        #         SUM(ST_Length(e.geometry)) AS total_length,
        #         ST_Union(e.geometry) AS geometry
        #     FROM
        #         {t}
        #         JOIN {edge_tables[i]} e ON e.source = ANY({t}.reachable_nodes::int[])
        #         AND e.target = ANY({t}.reachable_nodes::int[])
        #     WHERE
        #         start_node IN {ids_chunk}
        #     GROUP BY
        #         start_node
        # )
        # UPDATE
        #     {t}
        # SET
        #     reached_edges = j.reachable_edges,
        #     edge_length = j.total_length,
        #     coverage_area = ST_Area(ST_Buffer(j.geometry, {buffer_dist}))
        # FROM
        #     joined_edges j
        # WHERE
        #     {t}.start_node = j.start_node;"""

        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

        break

# %%
# **** COMPUT CONVEX HULL OF REACHABLE NODES ****

# for i, t in enumerate(table_names[0:1]):

#     print(f"At round: {i}")

#     # GET ALL IDS
#     df = pd.read_sql_query(f"SELECT node_id FROM {hex_tables[i]}", con=engine)
#     node_ids = tuple(df.node_id.to_list())

#     for ids_chunk in dbf.get_chunks(sequence=node_ids, chunk_size=1000):

#         # print(f"Computing convex hull for chunk: {ids_chunk}")

#         q1 = f"""CREATE TEMP TABLE temp_joined_nodes AS
#                 WITH joined_nodes AS (
#                     SELECT
#                         start_node,
#                         ST_ConcaveHull(ST_Collect(n.geometry), 0.2, FALSE) AS geometry
#                     FROM
#                         {t}
#                         JOIN nodes n ON n.id = ANY({t}.reachable_nodes::INT[])
#                     WHERE
#                         start_node IN {ids_chunk}
#                     GROUP BY
#                         start_node
#                 )
#             SELECT * FROM joined_nodes;"""

#         result = dbf.run_query_pg(q1, connection)
#         if result == "error":
#             print("Please fix error before rerunning and reconnect to the database")
#             break

#         q2 = f"""UPDATE
#                 {t} r
#             SET
#                 convex_hull = j.geometry,
#                 coverage_area = ST_Area(ST_Buffer(j.geometry,1))
#             FROM
#                 temp_joined_nodes j
#             WHERE
#                 r.start_node = j.start_node;"""

#         result = dbf.run_query_pg(q2, connection)
#         if result == "error":
#             print("Please fix error before rerunning and reconnect to the database")
#             break

#         q3 = """DROP TABLE temp_joined_nodes;"""

#         result = dbf.run_query_pg(q3, connection)
#         if result == "error":
#             print("Please fix error before rerunning and reconnect to the database")
#             break
# %%
connection.close()

# %%

with open("vacuum_analyze.py") as f:
    exec(f.read())

print("Script 05 complete!")
