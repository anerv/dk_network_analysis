# %%

from src import db_functions as dbf
import pandas as pd
import geopandas as gpd
import itertools

with open("vacuum_analyze.py") as f:
    exec(f.read())

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

# %%
engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%
run_pre = False

if run_pre:
    queries = [
        "sql/05a_prepare_reach_segments.sql",
        "sql/05b_compute_segment_topology.sql",
        "sql/05c_prepare_reach_edges_nodes.sql",
        "sql/05d_create_hexagon_centroids.sql",
    ]

    for i, q in enumerate(queries):
        print(f"Running step {i+1}...")
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

        print(f"Step {i+1} done!")

# %%
distances = [
    # 1,
    # 2,
    # 5,
    10,
    15,
]  # max distance in km

# %%
chunk_sizes_1 = [1000, 1000, 1000, 1000, 1000]
chunk_sizes_2 = [1000, 1000, 1000, 1000, 1000]
chunk_sizes_5 = [1000, 1000, 1000, 1000, 1000]
chunk_sizes_10 = [1000, 500, 200, 200, 200]
chunk_sizes_15 = [1000, 200, 100, 100, 100]

all_chunk_sizes = [
    # chunk_sizes_1,
    # chunk_sizes_2,
    # chunk_sizes_5,
    chunk_sizes_10,
    chunk_sizes_15,
]

# %%
edge_tables = [
    "reach.lts_1_segments",
    "reach.lts_1_2_segments",
    "reach.lts_1_3_segments",
    "reach.lts_1_4_segments",
    "reach.car_segments",
]

hex_tables = [
    "reach.hex_lts_1",
    "reach.hex_lts_2",
    "reach.hex_lts_3",
    "reach.hex_lts_4",
    "reach.hex_car",
]

for dist in distances:

    chunk_sizes = all_chunk_sizes[distances.index(dist)]

    print(f"Computing reach for distance: {dist} km")

    # REACH PARAMETERS
    table_names = [
        f"reach.lts_1_reach_{dist}",
        f"reach.lts_2_reach_{dist}",
        f"reach.lts_3_reach_{dist}",
        f"reach.lts_4_reach_{dist}",
        f"reach.car_reach_{dist}",
    ]

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

    # COMPUTE REACHABLE NODES USING CHUNKS

    for i, t in enumerate(table_names):

        print(f"At round: {i}")

        # GET ALL IDS
        df = pd.read_sql_query(f"SELECT node_id FROM {hex_tables[i]}", con=engine)
        node_ids = df.node_id.to_list()

        for ids_chunk in dbf.get_chunks(sequence=node_ids, chunk_size=chunk_sizes[i]):

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

    # **** COMPUT REACHABLE EDGES ****

    # Add new columns
    for t in table_names:

        q = f"""
            ALTER TABLE
                {t}
            ADD
                COLUMN IF NOT EXISTS reachable_edges VARCHAR DEFAULT NULL,
            ADD
                COLUMN IF NOT EXISTS edge_length NUMERIC DEFAULT NULL;
            """

        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    # compute reachable edges
    for i, t in enumerate(table_names):

        print(f"Computing edges: At round: {i}")

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
                        SUM(fe.length) AS total_length
                    FROM filtered_nodes fn
                    JOIN filtered_edges fe
                    ON fe.source = ANY(fn.reachable_nodes::int[])
                    AND fe.target = ANY(fn.reachable_nodes::int[])
                    GROUP BY fn.start_node
                )
                UPDATE {t} rc
                SET
                    reachable_edges = j.reachable_edges,
                    edge_length = j.total_length
                FROM joined_edges j
                WHERE rc.start_node = j.start_node;
            
            """

            result = dbf.run_query_pg(q, connection)
            if result == "error":
                print("Please fix error before rerunning and reconnect to the database")
                break

    # Join hex_id to reach tables
    for i, t in enumerate(table_names):
        q1 = f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS hex_id VARCHAR;"
        q2 = f"UPDATE {t} SET hex_id = h.hex_id FROM {hex_tables[i]} h WHERE {t}.start_node = h.node_id;"
        q3 = f"CREATE INDEX IF NOT EXISTS {network_levels_step[i]}_reach_{dist}_ix ON {t} (hex_id);"

        for q in [q1, q2, q3]:
            result = dbf.run_query_pg(q, connection)
            if result == "error":
                print("Please fix error before rerunning and reconnect to the database")
                break

    # prepare joined table
    prepare_hex_reach = [
        "CREATE INDEX IF NOT EXISTS hex_grid_ix ON hex_grid (hex_id);"
        f"DROP TABLE IF EXISTS reach.hex_reach_{dist};"
    ]

    for q in prepare_hex_reach:
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    # create joined table
    q_hex_reach = f"""
    CREATE TABLE reach.hex_reach_{dist} AS
    SELECT
        h.hex_id,
        h.geometry,
        l1.edge_length / 1000 AS lts_1_reach,
        l2.edge_length / 1000 AS lts_1_2_reach,
        l3.edge_length / 1000 AS lts_1_3_reach,
        l4.edge_length / 1000 AS lts_1_4_reach,
        ca.edge_length / 1000 AS car_reach
    FROM
        hex_grid h
        LEFT JOIN {table_names[0]} l1 ON h.hex_id = l1.hex_id
        LEFT JOIN  {table_names[1]} l2 ON h.hex_id = l2.hex_id
        LEFT JOIN  {table_names[2]} l3 ON h.hex_id = l3.hex_id
        LEFT JOIN  {table_names[3]} l4 ON h.hex_id = l4.hex_id
        LEFT JOIN  {table_names[4]} ca ON h.hex_id = ca.hex_id;
    """

    result = dbf.run_query_pg(q_hex_reach, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

    # Check if all hexagons are present
    q_check = f"""
    DO $$
    DECLARE
        hex_reach_len INT;

    DECLARE
        hex_grid_len INT;

    BEGIN
        SELECT
            COUNT(*) INTO hex_reach_len
        FROM
            reach.hex_reach_{dist};

    SELECT
        COUNT(*) INTO hex_grid_len
    FROM
        hex_grid;

    ASSERT hex_grid_len = hex_reach_len,
    'Missing hex cells!';

    END $$;
    """
    result = dbf.run_query_pg(q_check, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

    # compute difference between lts and car reach
    q_alter = f"""
    ALTER TABLE
        reach.hex_reach_{dist}
    ADD
        COLUMN car_lts_1_diff DECIMAL,
    ADD
        COLUMN car_lts_1_2_diff DECIMAL,
    ADD
        COLUMN car_lts_1_3_diff DECIMAL,
    ADD
        COLUMN car_lts_1_4_diff DECIMAL;"""

    q_update = f"""UPDATE
        reach.hex_reach_{dist}
    SET
        car_lts_1_diff = car_reach - lts_1_reach,
        car_lts_1_2_diff = car_reach - lts_1_2_reach,
        car_lts_1_3_diff = car_reach - lts_1_3_reach,
        car_lts_1_4_diff = car_reach - lts_1_4_reach;

    """

    for q in [q_alter, q_update]:
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")

    for n in network_levels_step:
        q = f"""
        UPDATE
            reach.hex_reach_{dist}
        SET
            {n}_reach = 0
        WHERE
            {n}_reach IS NULL;

        """

        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")

    # compute percentage difference between lts and car reach
    q_alter = f"""
    ALTER TABLE
        reach.hex_reach_{dist}
    ADD
        COLUMN car_lts_1_diff_pct DECIMAL,
    ADD
        COLUMN car_lts_1_2_diff_pct DECIMAL,
    ADD
        COLUMN car_lts_1_3_diff_pct DECIMAL,
    ADD
        COLUMN car_lts_1_4_diff_pct DECIMAL;
    """

    q_update = f"""UPDATE
        reach.hex_reach_{dist}
    SET
        car_lts_1_diff_pct = (lts_1_reach / car_reach) * 100,
        car_lts_1_2_diff_pct = (lts_1_2_reach / car_reach) * 100,
        car_lts_1_3_diff_pct = (lts_1_3_reach / car_reach) * 100,
        car_lts_1_4_diff_pct = (lts_1_4_reach / car_reach) * 100
    WHERE
        car_reach > 0;"""

    for q in [q_alter, q_update]:
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    for n in network_levels_step[:-1]:
        f"""
        UPDATE
            reach.hex_reach_{dist}
        SET
            car_{n}_diff_pct = 100
        WHERE
            car_reach = 0
            AND {n}_reach > 0;
        """
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    # combine results and join to hex grid
    q_drop = f"DROP TABLE IF EXISTS reach.reach_{dist}_component_length_hex;"

    q_create = f"""
    CREATE TABLE reach.reach_{dist}_component_length_hex AS (
        SELECT
            dens.hex_id,
            dens.lts_1_length,
            dens.lts_1_2_length,
            dens.lts_1_3_length,
            dens.lts_1_4_length,
            dens.total_car_length,
            dens.lts_1_dens,
            dens.lts_1_2_dens,
            dens.lts_1_3_dens,
            dens.lts_1_4_dens,
            dens.total_car_dens,
            dens.geometry,
            comp.component_1_count,
            comp.component_1_2_count,
            comp.component_1_3_count,
            comp.component_1_4_count,
            comp.component_car_count,
            reach.lts_1_reach,
            reach.lts_1_2_reach,
            reach.lts_1_3_reach,
            reach.lts_1_4_reach,
            reach.car_reach
        FROM
            density.density_hex dens
            LEFT JOIN fragmentation.component_count_hex comp ON dens.hex_id = comp.hex_id
            LEFT JOIN reach.hex_reach_{dist} reach ON dens.hex_id = reach.hex_id
    );
    """

    # for q in [q_drop, q_create, q_update]:
    for q in [q_drop, q_create]:
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

    for t in table_names:
        q = f"SELECT COUNT(*) FROM {t} WHERE cardinality(reachable_nodes::integer[]) = 1;"
        df = pd.read_sql_query(q, con=engine)
        print(f"{len(df)} hexagon(s) with only one reachable node in table {t}")

connection.close()

# %%
with open("vacuum_analyze.py") as f:
    exec(f.read())

# %%

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

distances = [1, 2, 5, 10, 15]  # max distance in km

result = dbf.run_query_pg("DROP TABLE IF EXISTS reach.compare_reach;", connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

start = f"CREATE TABLE reach.compare_reach AS (SELECT r{distances[0]}.hex_id, "
end = ");"

select_columns = ""

for d in distances:
    s = f"""r{d}.lts_1_reach AS lts_1_reach_{d}, r{d}.lts_1_2_reach AS lts_1_2_reach_{d}, r{d}.lts_1_3_reach AS lts_1_3_reach_{d}, r{d}.lts_1_4_reach AS lts_1_4_reach_{d}, r{d}.car_reach AS car_reach_{d},"""
    select_columns += s

from_q = f"FROM reach.hex_reach_{distances[0]} r{distances[0]}"

for d in distances[1:]:
    from_q += f" JOIN reach.hex_reach_{d} r{d} ON r{d}.hex_id = r{distances[0]}.hex_id"

final_query = start + select_columns[:-1] + " " + from_q + end

result = dbf.run_query_pg(final_query, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")


# ADD geometry column
q_geo = "ALTER TABLE reach.compare_reach ADD COLUMN geometry geometry;"
q_update = "UPDATE reach.compare_reach SET geometry = h.geometry FROM hex_grid h WHERE reach.compare_reach.hex_id = h.hex_id;"

for q in [q_geo, q_update]:
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break


# Compute percentage difference between reach values

for n in network_levels_step:

    for comb in itertools.combinations(distances, 2):

        q1 = f"ALTER TABLE reach.compare_reach ADD COLUMN IF NOT EXISTS {n}_pct_diff_{comb[0]}_{comb[1]} DECIMAL;"

        q2 = f"""UPDATE reach.compare_reach SET {n}_pct_diff_{comb[0]}_{comb[1]} = (({n}_reach_{comb[1]} - {n}_reach_{comb[0]})) / (({n}_reach_{comb[1]} + {n}_reach_{comb[0]})/2) * 100 WHERE {n}_reach_{distances[0]} > 0;"""
        for q in [q1, q2]:
            result = dbf.run_query_pg(q, connection)
            if result == "error":
                print("Please fix error before rerunning and reconnect to the database")
                break

# compute difference between reach values
for n in network_levels_step:

    for comb in itertools.combinations(distances, 2):

        q1 = f"ALTER TABLE reach.compare_reach ADD COLUMN IF NOT EXISTS {n}_diff_{comb[0]}_{comb[1]} DECIMAL;"

        q2 = f"UPDATE reach.compare_reach SET {n}_diff_{comb[0]}_{comb[1]} = {n}_reach_{comb[1]} - {n}_reach_{comb[0]} WHERE {n}_reach_{distances[0]} > 0;"

        for q in [q1, q2]:
            result = dbf.run_query_pg(q, connection)
            if result == "error":
                print("Please fix error before rerunning and reconnect to the database")
                break


# Compute average socio reach

q_socio = "sql/05e_compute_socio_reach.sql"
result = dbf.run_query_pg(q_socio, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

# compute socio reach comparison
q_socio_comparison = "sql/05f_compute_socio_reach_comparison.sql"
result = dbf.run_query_pg(q_socio_comparison, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

# get column names
hex_reach_comparison = gpd.read_postgis(
    "SELECT * FROM reach.compare_reach LIMIT 1;", engine, geom_col="geometry"
)

compare_columns = [c for c in hex_reach_comparison.columns if "pct_diff" in c]

q_start = """CREATE TABLE reach.socio_reach_comparison AS SELECT j.id,"""

q_end = """ FROM reach.joined j GROUP BY j.id;"""

select_columns = ""

for c in compare_columns:
    s = f"AVG(j.{c}) AS {c}_average, "
    select_columns += s

    s = f"MIN(j.{c}) AS {c}_min, "
    select_columns += s

    s = f"MAX(j.{c}) AS {c}_max, "
    select_columns += s

    s = f"PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY j.{c}) AS {c}_median, "
    select_columns += s

final_query = q_start + select_columns[:-2] + q_end

result = dbf.run_query_pg(final_query, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

q_socio_comparison_end = "sql/05g_finish_socio_reach_comparison.sql"
result = dbf.run_query_pg(q_socio_comparison_end, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

# %%

# drop preliminary tables
for d in distances:
    table_names = [
        f"reach.lts_1_reach_{dist}",
        f"reach.lts_2_reach_{dist}",
        f"reach.lts_3_reach_{dist}",
        f"reach.lts_4_reach_{dist}",
        f"reach.car_reach_{dist}",
    ]

    for t in table_names:
        q = f"DROP TABLE IF EXISTS {t};"
        result = dbf.run_query_pg(q, connection)
        if result == "error":
            print("Please fix error before rerunning and reconnect to the database")
            break

for e in edge_tables:
    q = f"DROP TABLE IF EXISTS {e};"
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

drop_tables = [
    "DROP TABLE IF EXISTS segment_nodes;",
    "DROP TABLE IF EXISTS edges_segments;",
]

for d in drop_tables:
    result = dbf.run_query_pg(d, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

with open("vacuum_analyze.py") as f:
    exec(f.read())

print("Script 05 complete!")
# %%
