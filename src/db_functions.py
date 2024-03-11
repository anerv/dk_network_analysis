"""
Functions for connecting and quering a postgresql database from python
Uses psycopg2 and sqlaclhemy
sqlaclemy is particularly useful for loading data without having to specifify column names and types in advance
"""

import psycopg2 as pg
import sqlalchemy

# TODO Format function docstrings to standard format


# Function for connecting to database using psycopg2
def connect_pg(
    db_name, db_user, db_password, db_port, db_host="localhost", print=False
):
    """
    Function for connecting to database using psycopg2
    Required input are database name, username, password
    If no host is provided localhost is assumed
    Returns the connection object
    """

    # Connecting to the database
    try:
        connection = pg.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )

        if print:
            print("You are connected to the database %s!" % db_name)

        return connection

    except (Exception, pg.Error) as error:
        print("Error while connecting to PostgreSQL", error)


# Function for running sql query using psycopg2
def run_query_pg(query, connection):
    """Function for running a sql query using psycopg2"""

    cursor = connection.cursor()
    # Check whether query is a sql statement as string or a filepath to an sql file
    query_is_file = query.endswith(".sql")

    if query_is_file:
        open_query = open(query, "r")
        try:
            cursor.execute(open_query.read())
        except Exception as e:
            print(e)

            cursor.close()
            connection.close()
            return "error"
    else:
        try:
            cursor.execute(query)
        except Exception as e:
            print(e)

            cursor.close()
            connection.close()
            return "error"

    try:
        result = cursor.fetchall()
    except:
        result = None

    connection.commit()
    cursor.close()
    return result


# def run_query_pg(
#     query,
#     connection,
#     success="Query successful!",
#     fail="Query failed!",
#     commit=True,
#     close=False,
# ):
#     """
#     Function for running a sql query using psycopg2
#     Required input are query/filepath (string) to query and name of database connection
#     Optional input are message to be printed when the query succeeds or fails, and whether the function should commit the changes (default is to commit)
#     You must be connected to the database before using the function
#     """

#     cursor = connection.cursor()

#     # Check whether query is a sql statement as string or a filepath to an sql file
#     query_is_file = query.endswith(".sql")

#     try:
#         if query_is_file:
#             open_query = open(query, "r")
#             cursor.execute(open_query.read())
#         else:
#             cursor.execute(query)

#         print(success)

#         try:
#             result = cursor.fetchall()
#             rows_changed = len(result)
#             print(rows_changed, "rows were updated or retrieved")
#             return result
#         except:
#             pass

#         if commit:
#             connection.commit()
#             print("Changes commited")
#         else:
#             print("Changes not commited")
#         if close:
#             connection.close()
#             print("Connection closed")

#     except Exception as error:
#         print(fail)
#         print(error)
#         print("Please fix error before rerunning and reconnect to the database")
#         connection.close()

#         return "error"

#         """
#         try:
#             connection = pg.connect(database = db_name, user = db_user,
#                                         password = db_password,
#                                         host = db_host)
#             print('You are connected to the database %s!' % db_name)
#         except (Exception, pg.Error) as error :
#             print("Error while connecting to PostgreSQL", error)
#         """


# Function for connecting to database using sqlalchemy
def connect_alc(db_name, db_user, db_password, db_port, db_host="localhost"):
    """
    Function for connecting to database using sqlalchemy
    Required input are database name, username, password
    If no host is provided localhost is assumed
    Returns the engine object
    """

    # Create engine
    engine_info = (
        "postgresql://"
        + db_user
        + ":"
        + db_password
        + "@"
        + db_host
        + ":"
        + db_port
        + "/"
        + db_name
    )

    # Connecting to database
    try:
        engine = sqlalchemy.create_engine(engine_info)
        engine.connect()
        print("You are connected to the database %s!" % db_name)
        return engine
    except (Exception, sqlalchemy.exc.OperationalError) as error:
        print("Error while connecting to the dabase!", error)


# Function for loading data to database using sqlalchemy
def to_postgis(geodataframe, table_name, engine, if_exists="replace", schema=None):
    """
    Function for loading a geodataframe to a postgres database using sqlalchemy
    Required input are geodataframe, desired name of table and sqlalchemy engine
    Default behaviour is to replace table if it already exists, but this can be changed to fail
    """

    try:
        geodataframe.to_postgis(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists=if_exists,
        )
        print(table_name, "successfully loaded to database!")
    except Exception as error:
        print("Error while uploading data to database:", error)


# Function for running query using sqlalchemy
def run_query_alc(query, engine, success="Query successful!", fail="Query failed!"):
    with engine.connect() as connection:
        try:
            result = connection.execute(query)
            print(success)
            return result
        except Exception as error:
            print(fail)
            print(error)


if __name__ == "__main__":
    db_user = "postgres"
    db_password = "aneitu"
    db_host = "localhost"
    db_name = "bike_network"
    db_port = "5432"

    connection = connect_pg(db_name, db_user, db_password)

    q1 = "CREATE TABLE IF NOT EXISTS test_table (test_col VARCHAR);"
    q2 = "INSERT INTO test_table VALUES ('bike');"
    q3 = "DROP TABLE IF EXISTS test_table CASCADE;"

    q4 = "../tests/test_sql.sql"

    test1 = run_query_pg(q1, connection, commit=True)
    test2 = run_query_pg(q2, connection, commit=True)
    test3 = run_query_pg(q3, connection, commit=True)
    test4 = run_query_pg(q4, connection, commit=True)

    engine_test = connect_alc(db_name, db_user, db_password, db_port=db_port)

    q5 = """CREATE TABLE IF NOT EXISTS test_table2 (test_col VARCHAR);
            INSERT INTO test_table2 VALUES ('bike');"""

    q6 = "DROP TABLE IF EXISTS test_table2 CASCADE;"

    test5 = run_query_alc(q5, engine_test)
    test6 = run_query_alc(q6, engine_test)
