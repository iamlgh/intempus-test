import json
import shared

def genDbUpdate(upd2Db, dbId = None):
    setTxt = ""
    for key in upd2Db:
        if key == 'id':
            if dbId:
                where = f"WHERE id={dbId}"
                if setTxt:
                    setTxt += ", "
                setTxt += f"{key}={upd2Db[key]}"
            else:
                where = f"WHERE {key}={upd2Db[key]}"
        elif key == 'responsibles' and upd2Db[key] == None:
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}=ARRAY[]::VARCHAR[]"
        elif key == 'responsibles':
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}=ARRAY{upd2Db[key]}::VARCHAR[]"
        elif type(upd2Db[key]) is str or type(upd2Db[key]) is None:
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}='{upd2Db[key]}'"
        else:
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}={upd2Db[key]}"
    setTxt = "SET " + setTxt
    updateStr = f"UPDATE projects {setTxt} {where}"
    return updateStr

def insertInDb(cursor, jsonRecord):
    rv = shared.runSql(cursor, f"INSERT INTO {shared.MAIN_TABLE} SELECT * FROM json_populate_record(NULL::{shared.MAIN_TABLE}, '{jsonRecord}') RETURNING *;")
    return rv

def updateDb(cursor, upd2Db, dbId = None):
    if dbId:
        print(f"Update db project {dbId} to {upd2Db['id']}")
    updateCmd = genDbUpdate(upd2Db, dbId)
    print(updateCmd)
    rv = shared.runSql(cursor, updateCmd)
    return rv

connection = shared.connectDb()
cursor = connection.cursor()
j = {}
j['id'] = 9612054
j['responsibles'] = []
print(j['responsibles'])
rv = updateDb(cursor, j)
print(rv)

with open("./data/params_updated_after_add.json", "r", encoding="utf-8") as jsonData:
    upd2Db = json.load(jsonData)
print(genDbUpdate(upd2Db, 1))
print(genDbUpdate(upd2Db))