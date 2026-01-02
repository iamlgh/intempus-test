import json
import shared

def readIntempusInit():
    print("FROM FILE A initial.json")
    with open("./data/initial.json", "r", encoding="utf-8") as projectsJson:
        projects = json.load(projectsJson)
    print(f"Intempus object count: {projects['meta']['total_count']}")
    #print(projects['objects'])
    return projects

def readIntempusUpd():
    print("FROM FILE A update.json")
    with open("./data/update.json", "r", encoding="utf-8") as projectsJson:
        projects = json.load(projectsJson)
    print(f"Intempus object count: {projects['meta']['total_count']}")
    #print(projects['objects'])
    return projects

def readDbUpd():
    print("FROM FILE B update.json")
    with open("./data/project_update_after_add.json", "r", encoding="utf-8") as projectsJson:
        projects = json.load(projectsJson)
    print(f"DB object count: {projects['meta']['total_count']}")
    #print(projects['objects'])
    return projects

#shared.insertInDb(cursor, '{"id":1,"customer":"/web/v1/customer/6666940/","customer_id":"6666940","number":"7","name":"Example 7","file_upload_required":false,"active":false,"notes":"these are my notes"}')

def processUpdates(data):
    updatesIntempus2Db = data[0]
    addsIntempus2Db = data[1]
    deletesIntempus2Db = data[2]
    updatesDb2Intempus = data[3]
    addsDb2Intempus = data[4]
    deletesDb2Intempus = data[5]
    connection = shared.connectDb()
    cursor = connection.cursor()
    rv = 0
    #print("addsIntempus2Db", addsIntempus2Db) #add specified project to db
    for add2Db in addsIntempus2Db:
        rv += insertInDb(cursor, json.dumps(add2Db))
    #print("updatesIntempus2Db", updatesIntempus2Db) #update project in db, with updated values
    for upd2Db in updatesIntempus2Db:
        rv += updateDb(cursor, upd2Db)
    #print("deletesIntempus2Db", deletesIntempus2Db) #delete specified project from db
    for del2Db in deletesIntempus2Db:
        rv += deleteFromDb(cursor, delDb)
    #print("addsDb2Intempus", addsDb2Intempus) #add project to Intempus, then update db with all values for the specified projects (requires customer and customer_id)
    for add2Intempus in addsDb2Intempus:
        rv += addToIntempus(cursor, add2Intempus)
    #print("updatesDb2Intempus", updatesDb2Intempus) #update project in Intempus, with updated values
    for upd2Intempus in updatesDb2Intempus:
        rv += updateIntempus(cursor, upd2Intempus)
    #print("deletesDb2Intempus", deletesDb2Intempus) #delete project from Intempus, then from db, for the specified projects
    for delIntempus in deletesDb2Intempus:
        rv += deleteFromDb(cursor, delIntempus)
    connection.close()
    return rv