import os
import psycopg2
import warnings

MAIN_TABLE = "projects"
ID_COL_NAME = "project_id"
DB_SCRIPT = "CreateProjectsTable.sql"

def connectDb():
    # read environment variables
    dbUser = os.getenv('POSTGRES_USER')
    dbPassword = os.getenv('POSTGRES_PASSWORD')
    dbName = os.getenv('POSTGRES_DB')
    dbHost = os.getenv('POSTGRES_HOST')

    # Checking if an environment variable exists
    if not dbName:
        print("DB name not found")
    if not dbUser:
        print("DB user not found")
    if not dbPassword:
        print("DB password not found")
    if not dbHost:
        print("DB host not found, using local")

    try:
        connection = psycopg2.connect(database=dbName, user=dbUser, password=dbPassword, host=dbHost, port=5432)
        connection.autocommit = True
    except psycopg2.OperationalError as e:
        raise SystemExit("Can't connect to DB:", e)
    except Exception as e:
        print ("Exception type:", type(e))
        raise SystemExit("Unknown error connecting to DB")
    return connection

def runSql(cursor, sql):
    try:
        #print(sql)
        cursor.execute(sql)
    except (psycopg2.OperationalError, psycopg2.DataError, psycopg2.DatabaseError, psycopg2.ProgrammingError) as e:
        warnings.warn(e)
        return 1
    except Exception as e:
        print ("Exception type:", type(e))
        raise SystemExit("Unknown error running runSql")
    return 0

def createProjectsTable(cursor):
    #verify MAIN_TABLE exists, otherwise create it
    rv = runSql(cursor, f"SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public' AND tablename='{MAIN_TABLE}';")
    if not rv:
        row = cursor.fetchone()
        if not row:
            print(f"Create {MAIN_TABLE} table from {DB_SCRIPT}")
            try:
                rv = cursor.execute(open(DB_SCRIPT, "r").read())
            except Exception as e:
                print ("Exception type:", type(e))
                print(rv)
                raise SystemExit(f"Unable to verify or create {MAIN_TABLE}")
    return 0
