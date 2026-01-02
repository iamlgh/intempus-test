import shared
import os

def test_createProjectsTable():
    os.environ['POSTGRES_USER'] = 'postgres'
    os.environ['POSTGRES_PASSWORD'] = 'postgres'
    os.environ['POSTGRES_DB'] = 'systemb'
    os.environ['POSTGRES_HOST'] = 'localhost'
    connection = shared.connectDb()
    cursor = connection.cursor()
    assert shared.createProjectsTable(cursor) == 0
    connection.close()


def test_runSql():
    connection = shared.connectDb()
    cursor = connection.cursor()
    sql = f"SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public' AND tablename='{shared.MAIN_TABLE}';"
    assert shared.runSql(cursor, sql) == 0
    connection.close()

