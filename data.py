# this script creates an sql script used to create the "projects" table for System B
import json
import re
import shared
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='data.log', encoding='utf-8', level=logging.DEBUG)

with open("./data/data.json", "r") as file:
    data = json.load(file)

if data:
    dataType = "str"
    pyToDB = {
        "str": "VARCHAR(255)",
        "date": "DATE",
        "int": "INT",
        "bigint": "BIGINT",
        "list": "text[]",
        "NoneType": "VARCHAR(255)",
        "bool": "BOOLEAN",
        "float": "NUMERIC"
    }
    f = open(shared.DB_SCRIPT, "x", encoding="utf-8")
    if f:
        logger.debug(f"CREATE TABLE {shared.MAIN_TABLE} (")
        f.write(f"CREATE TABLE {shared.MAIN_TABLE} (")
        f.write("\n")
        lists = ""
        dbTables = []

        for key in data.keys():
            classedDataType = type(data[key])
            dataType = re.findall("'[^']+'", str(classedDataType))
            dataType = dataType[0].strip("'")

            #handle type exceptions that the sample output didn't contain
            if key == "logical_timestamp":
                dataType = "bigint"
            elif key == "feofence":
                dataType = "bool"
            elif re.search("(longitude|latitude|hour_budget)$", key):
                dataType = "float"
            elif re.search("_date$", key):
                dataType = "date"

            #nake id a required value
            notNull = ""
            if key == "id":
                notNull = " NOT NULL UNIQUE"

            #write each column 
            logger.debug("    " + key + " " + pyToDB.get(dataType) + notNull + ",")
            f.write("    " + key + " " + pyToDB.get(dataType) + notNull + ",")
            f.write("\n")

        logger.debug("    PRIMARY KEY (id)")
        logger.debug(");")
        logger.debug(lists)
        f.write("    PRIMARY KEY (id)")
        f.write("\n")
        f.write(");")
        f.write("\n")
        f.write(lists)
        f.write("\n")
        f.close()
