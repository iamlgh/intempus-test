import json
import os
import requests
import shared
from psycopg2.extras import RealDictCursor

def compareKeys(keysL, keysR, nameL = "Left", nameR = "Right"):
    #are keys between the two systems the same
    keysL = sorted(keysL) #objD.keys()
    keysR = sorted(keysR)
    rv = None
    if keysL != keysR:
        print ("WARNING: Keys are not the same")
        uniqueKeysL = set(keysL) - set(keysR)
        if uniqueKeysL:
            print(f"Keys only in {nameL}: {uniqueKeysL}")
        uniqueKeysR = set(keysR) - set(keysL)
        if uniqueKeysR:
            print(f"Keys only in {nameR}: {uniqueKeysR}")
        rv = (uniqueKeysL, uniqueKeysR)
    return rv

def getProjectChanges(objFrom, objTo):
    j = {}
    for key in objTo.keys():
        #include the keys with differences
        if objTo[key] != objFrom[key]:
            # in case db is null instead of empty array
            if key == 'responsibles' and type(objTo[key]) is not type(objFrom[key]):
                j[key] = objFrom[key]
            # elifs handle keys where the data is the same but doesn't look the same becaise of type differences
            # and only include them if they are different after formatting
            elif key == 'hour_budget' and type(objTo[key]) is not type(objFrom[key]):
                if type(objFrom[key]) is float:
                    if objTo[key] != ("{:.2f}".format(objFrom[key])):
                        j[key] = objFrom[key]
                elif type(objTo[key]) is float:
                    if objFrom[key] != ("{:.2f}".format(objTo[key])):
                        j[key] = objFrom[key]
            elif type(objTo[key]) is not type(objFrom[key]):
                # null to object or vice-versa
                if objTo[key] is None or objFrom[key] is None:
                    j[key] = objFrom[key]
                # for longitute and latitude where a value exists for both, the types will be different (float vs str)
                # and the float value has to be formatted (as str) before comparing
                elif type(objFrom[key]) is float:
                    if objTo[key] != ("{:.6f}".format(objFrom[key])):
                        j[key] = objFrom[key]
                elif type(objTo[key]) is float:
                    if objFrom[key] != ("{:.6f}".format(objTo[key])):
                        j[key] = objFrom[key]
            # normal differences
            else:
                j[key] = objFrom[key]
    return j

def checkForChanges(objD, objI):
    updatesDb2Intempus = []
    updatesIntempus2Db = []
    j = None
    #print("Checking if change was to db data or Intempus data")
    # the DB doesn't update logical_timestamp so the logical_timestamps will be equal if there is only a DB update
    if objD['logical_timestamp'] == objI['logical_timestamp']:
        compareKeys(objD.keys(), objI.keys(), "db", "Intempus")
        # compare values for every key, but update changes only
        j = getProjectChanges(objD, objI)
        if j:    
            print("db data changed")
            j['id'] = objD['id']
            j['resource_uri'] = objD['resource_uri']
            updatesDb2Intempus.append(j)
    # If Intempus data has changed, the logical_timestamp will be higher than the value in the DB
    elif objD['logical_timestamp'] != objI['logical_timestamp']:
        compareKeys(objI.keys(), objD.keys(), "Intempus", "db")
        # compare values for every key, but update changes only
        j = getProjectChanges(objI,objD)
        if j:    
            print("Intempus data changed")
            j['id'] = objI['id']
            j['resource_uri'] = objI['resource_uri']
            updatesIntempus2Db.append(j)
    #else:
    #    raise SystemExit("Cannot determine which data has changed")
    if j:
        print(f"Need to update Id {objI['id']}")
    else:
        print(f"Unchanged {objD['id']}")
    return(updatesDb2Intempus, updatesIntempus2Db)

def parseData(dbData, iData):
    updatesIntempus2Db = [] #update project in db, with updated values
    addsIntempus2Db = [] #add specified project to db
    updatesDb2Intempus = [] #update project in Intempus, with updated values
    addsDb2Intempus = [] #add project to Intempus, then update db with all values for the specified projects (requires customer and customer_id)
    if dbData and iData['objects']:
        print("Check for differences between systems")
        #with open('./data/end_db_data.json', 'w') as fp:
        #    json.dump(dbData, fp)
        if not dbData == iData['objects']:
            #print("Systems have differences")
            for objI in iData['objects']:
                print(f"Looking for project {objI['id']} in db")
                found = 0
                for objD in dbData:
                    if objD['id'] and objD['id'] == objI['id']:
                        print(f"Found {objD['id']}")
                        found = 1
                        break

                if found:
                    if objI == objD:
                        print(f"Unchanged {objD['id']}")
                    else:
                        #with open(f'./data/{objD['id']}_B_data.json', 'w') as fp:
                        #    json.dump(objD, fp)
                        #with open(f'./data/{objD['id']}_A_data.json', 'w') as fp:
                        #    json.dump(objI, fp)
                        updates = checkForChanges(objD, objI)
                        updatesDb2Intempus = updates[0]
                        updatesIntempus2Db = updates[1]
                else:
                    print(f"Need to add project {objI['id']} to db")
                    addsIntempus2Db.append(objI)
                
            for objD in dbData:
                #look for new db entries
                print(f"Looking for project {objD['id']} in Intempus")
                found = 0
                for objI in iData['objects']:
                    if objI['id'] and objD['resource_uri'] and objD['id'] == objI['id'] and objD['resource_uri'] == objI['resource_uri']:
                        print(f"Found {objD['id']}")
                        found = 1
                        break

                if not found:
                    print(f"It looks like the DB entry with id={objD['id']} is new and not in Intempus.")
                    addsDb2Intempus.append(objD)
        else:
            print("No changes found")
    elif iData['objects']:
        # copy all data to DB
        print("Need to add all projects to db")
        addsIntempus2Db = iData['objects']
    data = (updatesIntempus2Db, addsIntempus2Db, updatesDb2Intempus, addsDb2Intempus)
    return data

def processUpdates(data):
    updatesIntempus2Db = data[0]
    addsIntempus2Db = data[1]
    updatesDb2Intempus = data[2]
    addsDb2Intempus = data[3]
    connection = shared.connectDb()
    cursor = connection.cursor()
    rv = 0
    
    #add specified project to db
    for add2Db in addsIntempus2Db:
        rv += insertInDb(cursor, json.dumps(add2Db))
    #update project in db, with updated values
    for upd2Db in updatesIntempus2Db:
        rv += updateDb(cursor, upd2Db)
    #add project to Intempus, then update db with all values for the specified projects (requires customer and customer_id)
    for add2Intempus in addsDb2Intempus:
        rv += addToIntempus(cursor, add2Intempus)
    #update project in Intempus, with updated values
    for upd2Intempus in updatesDb2Intempus:
        rv += updateIntempus(cursor, upd2Intempus)
    connection.close()
    return rv
      
def readIntempus():
    # get all projects (if there are a lot of projects, then possibly get only projects updated after a the last run date)
    print("FROM A")
    url = "https://intempus.dk/web/v1/case/"
    apikey = os.environ['INTEMPUS_APIKEY']
    user = os.environ['INTEMPUS_USER']
    headers = {'authorization': f'apikey {user}:{apikey}', 'accept': 'application/json'}
    r = requests.get(url, headers=headers)
    projects = None
    if r.ok:
        projects = r.json()
    return r, projects

def readDb():
    # get all projects (if there are a lot of projects, then possibly get only projects updated after a the last run date)
    print("FROM B")
    connection = shared.connectDb()
    cursor = connection.cursor()
    
    #the "projects" table will be ceated if it doesn't exist in the DB
    shared.createProjectsTable(cursor)
    projects = []

    # request data returned as json for easiest conversion to a list of dictionaries
    curdict = connection.cursor(cursor_factory=RealDictCursor)
    rv = shared.runSql(curdict, f"SELECT row_to_json(r) project FROM (SELECT * FROM {shared.MAIN_TABLE} ORDER by id) r;")
    if not rv:
        dbData = curdict.fetchall()
        connection.close()
        if len(dbData):
            #with open('./data/db_data_row_to_json.json', 'w') as fp:
            #    json.dump(dbData, fp)
            # dbData is a list where each row is a dict in a "project" dict, but it is easier to compare to the Intempus 
            # result, if a list of dictionaries is used
            for row in dbData:
                print(f"Project id {row['project']['id']}")
                projects.append(row['project'])
    return rv, projects

def genDbUpdate(upd2Db, dbId = None):
    setTxt = ""
    for key in upd2Db:
        if key == 'id':
            if dbId:
                #intentionally renaming id for a project added to the db, then synced to Intempus
                where = f"WHERE id={dbId}"
                if setTxt:
                    setTxt += ", "
                setTxt += f"{key}={upd2Db[key]}"
            else:
                where = f"WHERE {key}={upd2Db[key]}"
        elif key == 'responsibles' and upd2Db[key] is None:
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}=ARRAY[]::VARCHAR[]"
        elif key == 'responsibles':
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}=ARRAY{upd2Db[key]}::VARCHAR[]"
        elif type(upd2Db[key]) is str:
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}='{upd2Db[key]}'"
        elif upd2Db[key] is None:
            if setTxt:
                setTxt += ", "
            setTxt += f"{key}=NULL"
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
    #print(updateCmd)
    rv = shared.runSql(cursor, updateCmd)
    return rv

def addToIntempus(cursor, payload):
    url = "https://intempus.dk/web/v1/case/"
    apikey = os.environ['INTEMPUS_APIKEY']
    user = os.environ['INTEMPUS_USER']
    headers = {'authorization': f'apikey {user}:{apikey}', 'accept': 'application/json', 'content-type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    if r.ok:
        project = r.json()
        #with open('./data/payload_add.json', 'w') as fp:
        #    json.dump(payload, fp)
        #with open('./data/project_add.json', 'w') as fp:
        #    json.dump(project, fp)

        #compare payload to project and update db in order to make sure that default intempus data is added to the db
        upd2Db = getProjectChanges(project, payload)
        if (upd2Db):
            #with open('./data/params_updated_after_add.json', 'w') as fp:
            #    json.dump(upd2Db, fp)
            rv = updateDb(cursor, upd2Db, payload['id'])
            if rv:
                print("DB Update Failed")
    else:
        print("Intempus Update Failed")
        print(r.text)
        print(r.reason)
        rv = 1
    return rv

def updateIntempus(cursor, payload):
    url = f"https://intempus.dk{payload['resource_uri']}"
    apikey = os.environ['INTEMPUS_APIKEY']
    user = os.environ['INTEMPUS_USER']
    headers = {'authorization': f'apikey {user}:{apikey}', 'accept': 'application/json', 'content-type': 'application/json'}
    rv = 0
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    if r.ok:
        project = r.json()
        upd2Db = getProjectChanges(project, payload)
        if upd2Db:
            rv = updateDb(cursor, upd2Db, payload['id'])
        if rv:
            print("DB Update Failed")
    else:
        print("Intempus Update Failed")
        print(r.text)
        print(r.reason)
        rv = 1
    return rv

def main():
    print("Hello from intempus-test!")
    rv, dbData = readDb() # get projects from DB
    r, iData = readIntempus() # get projects from Intempus
    data = parseData(dbData, iData)
    rv = processUpdates(data)
    if rv:
        print(rv)
        raise SystemExit(f"Error processing updates {rv}")
    return

if __name__ == "__main__":
    main()
    print("Script Complete")