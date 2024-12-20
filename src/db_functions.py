"""
Functions for connecting and quering a postgresql database from python
Uses psycopg2 and sqlaclhemy
sqlaclemy is particularly useful for loading data without having to specifify column names and types in advance
"""

import psycopg2 as pg
import sqlalchemy
from typing import Any, Sequence, Iterator


def get_chunks(sequence: Sequence[Any], chunk_size: int) -> Iterator[Any]:
    for i in range(0, len(sequence), chunk_size):
        yield sequence[i : i + chunk_size]


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
