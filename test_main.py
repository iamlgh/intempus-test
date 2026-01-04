import main
import shared
import json
import os
import requests

from psycopg2.extras import RealDictCursor


def data_comparison_input():
    with open("./data/9611850_A_data.json", "r", encoding="utf-8") as jsonData:
        aObj = json.load(jsonData)
    with open("./data/9611850_B_data.json", "r", encoding="utf-8") as jsonData:
        bObj = json.load(jsonData)
    return aObj, bObj

def test_compareKeys():
    (aObj, bObj) = data_comparison_input()
    aObj['new_field'] = None
    (a, b) = main.compareKeys(aObj, bObj, "A", "B")
    assert len(a) == 1
    assert len(b) == 0

def test_getProjectChanges():
    #load a dump
    with open("./data/initial.json", "r", encoding="utf-8") as jsonData:
        aData = json.load(jsonData)
    #load b dump
    with open("./data/initial_upd_case.json", "r", encoding="utf-8") as jsonData:
        bData = json.load(jsonData)
    # load expected differences for update adding case_group, case_state, department from db
    with open("./data/diff_upd_case.json", "r", encoding="utf-8") as jsonData:
        diffData = json.load(jsonData)
    assert main.getProjectChanges(bData[1],aData['objects'][1]) == diffData
    # load expected differences for update to db with same data (clears values)
    assert main.getProjectChanges(aData['objects'][1],bData[1]) == {'case_group': None, 'case_state': None, 'department': None}

def test_getProjectChangesAtoB():
    # compare exceptions
    aObj, bObj = data_comparison_input()
    assert main.getProjectChanges(aObj, bObj) == {}

def test_getProjectChangesBtoA():
    # compare exceptions
    aObj, bObj = data_comparison_input()
    assert main.getProjectChanges(bObj, aObj) == {}

def input_to_parse_data():
    with open("./data/db_data_2_prj.json", "r", encoding="utf-8") as jsonData:
        dbData = json.load(jsonData)
    with open("./data/initial.json", "r", encoding="utf-8") as jsonData:
        iData = json.load(jsonData)
    data = main.parseData(dbData, iData)
    return data

def test_parseData1():
    #updated projects from Intempus to DB
    data = input_to_parse_data()
    assert data[0] == [{'active': True, 'creation_date': '2025-12-08', 'logical_timestamp': 9083590838, 'id': 9584678, 'resource_uri': '/web/v1/case/9584678/'}]

def test_parseData2():
    #added projects from Intempus to DB
    data = input_to_parse_data()
    assert data[1] == []

def test_parseData3():
    #updated projects from DB to Intempus
    data = input_to_parse_data()
    assert data[2] == []

def test_parseData4():
    #added projects from DB to Intempus
    data = input_to_parse_data()
    assert data[3] == [{'active': True, 'all_employees_may_add_work_reports': False, 'all_worktypes_may_used_in_work_reports': False, 'case_group': '/web/v1/case_group/16694/', 'case_group_full': '/web/v1/case_group/16694/', 'case_state': '/web/v1/case_state/4131/', 'case_state_id': '4131', 'case_state_name': 'Project State 1', 'city': 'a', 'co_responsible': None, 'co_responsible_id': None, 'co_responsible_name': None, 'country': 'a', 'creation_date': '2025-12-31', 'creation_id': None, 'customer': '/web/v1/customer/6666940/', 'customer_city': '', 'customer_country': 'DK', 'customer_id': '6666940', 'customer_latitude': None, 'customer_longitude': None, 'customer_name': 'Eksempelkunde', 'customer_street_address': 'Eksempelvej', 'customer_zip_code': '', 'department': '/web/v1/department/149056/', 'department_id': '149056', 'department_name': 'Department 1', 'end_date': None, 'file_upload_required': True, 'geofence': False, 'hour_budget': 155.5, 'id': 9601184, 'latitude': 55.6238, 'logical_timestamp': 9110908870, 'longitude': 12.5942, 'name': 'Sample 3a', 'notes': 'these are my notesa', 'number': '3a', 'number_of_children': 0, 'parent': None, 'parent_name': None, 'permit_new_workreports': False, 'priority': None, 'remarks_required': True, 'resource_uri': '/web/v1/case/9601184/', 'responsible': None, 'responsible_id': None, 'responsible_name': None, 'responsibles': [], 'root_parent': None, 'start_date': None, 'street_address': 'a', 'uuid': None, 'zip_code': 'a'}, {'active': False, 'all_employees_may_add_work_reports': False, 'all_worktypes_may_used_in_work_reports': True, 'case_group': None, 'case_group_full': None, 'case_state': None, 'case_state_id': None, 'case_state_name': None, 'city': '', 'co_responsible': None, 'co_responsible_id': None, 'co_responsible_name': None, 'country': '', 'creation_date': '2026-01-01', 'creation_id': None, 'customer': '/web/v1/customer/6666940/', 'customer_city': '', 'customer_country': 'DK', 'customer_id': '6666940', 'customer_latitude': None, 'customer_longitude': None, 'customer_name': 'Eksempelkunde', 'customer_street_address': 'Eksempelvej', 'customer_zip_code': '', 'department': None, 'department_id': None, 'department_name': None, 'end_date': None, 'file_upload_required': False, 'geofence': False, 'hour_budget': None, 'id': 9611715, 'latitude': None, 'logical_timestamp': 9113243275, 'longitude': None, 'name': 'Sample 5', 'notes': 'these are my 5 notes', 'number': '4', 'number_of_children': 0, 'parent': None, 'parent_name': None, 'permit_new_workreports': True, 'priority': None, 'remarks_required': None, 'resource_uri': '/web/v1/case/9611715/', 'responsible': None, 'responsible_id': None, 'responsible_name': None, 'responsibles': [], 'root_parent': None, 'start_date': None, 'street_address': '', 'uuid': None, 'zip_code': ''}, {'active': False, 'all_employees_may_add_work_reports': False, 'all_worktypes_may_used_in_work_reports': True, 'case_group': None, 'case_group_full': None, 'case_state': None, 'case_state_id': None, 'case_state_name': None, 'city': '', 'co_responsible': None, 'co_responsible_id': None, 'co_responsible_name': None, 'country': '', 'creation_date': '2026-01-01', 'creation_id': None, 'customer': '/web/v1/customer/6666940/', 'customer_city': '', 'customer_country': 'DK', 'customer_id': '6666940', 'customer_latitude': None, 'customer_longitude': None, 'customer_name': 'Eksempelkunde', 'customer_street_address': 'Eksempelvej', 'customer_zip_code': '', 'department': None, 'department_id': None, 'department_name': None, 'end_date': None, 'file_upload_required': False, 'geofence': False, 'hour_budget': None, 'id': 9611779, 'latitude': None, 'logical_timestamp': 9113263994, 'longitude': None, 'name': 'Example 5', 'notes': 'these are my 5 notes', 'number': '5', 'number_of_children': 0, 'parent': None, 'parent_name': None, 'permit_new_workreports': True, 'priority': None, 'remarks_required': None, 'resource_uri': '/web/v1/case/9611779/', 'responsible': None, 'responsible_id': None, 'responsible_name': None, 'responsibles': [], 'root_parent': None, 'start_date': None, 'street_address': '', 'uuid': None, 'zip_code': ''}, {'active': False, 'all_employees_may_add_work_reports': False, 'all_worktypes_may_used_in_work_reports': True, 'case_group': None, 'case_group_full': None, 'case_state': None, 'case_state_id': None, 'case_state_name': None, 'city': '', 'co_responsible': None, 'co_responsible_id': None, 'co_responsible_name': None, 'country': '', 'creation_date': '2026-01-01', 'creation_id': None, 'customer': '/web/v1/customer/6666940/', 'customer_city': '', 'customer_country': 'DK', 'customer_id': '6666940', 'customer_latitude': None, 'customer_longitude': None, 'customer_name': 'Eksempelkunde', 'customer_street_address': 'Eksempelvej', 'customer_zip_code': '', 'department': None, 'department_id': None, 'department_name': None, 'end_date': None, 'file_upload_required': False, 'geofence': False, 'hour_budget': None, 'id': 9611780, 'latitude': None, 'logical_timestamp': 9113267472, 'longitude': None, 'name': 'Example 6', 'notes': 'these are my 5 notes', 'number': '6', 'number_of_children': 0, 'parent': None, 'parent_name': None, 'permit_new_workreports': True, 'priority': None, 'remarks_required': None, 'resource_uri': '/web/v1/case/9611780/', 'responsible': None, 'responsible_id': None, 'responsible_name': None, 'responsibles': [], 'root_parent': None, 'start_date': None, 'street_address': '', 'uuid': None, 'zip_code': ''}, {'active': False, 'all_employees_may_add_work_reports': False, 'all_worktypes_may_used_in_work_reports': True, 'case_group': None, 'case_group_full': None, 'case_state': None, 'case_state_id': None, 'case_state_name': None, 'city': '', 'co_responsible': None, 'co_responsible_id': None, 'co_responsible_name': None, 'country': '', 'creation_date': '2026-01-01', 'creation_id': None, 'customer': '/web/v1/customer/6666940/', 'customer_city': '', 'customer_country': 'DK', 'customer_id': '6666940', 'customer_latitude': None, 'customer_longitude': None, 'customer_name': 'Eksempelkunde', 'customer_street_address': 'Eksempelvej', 'customer_zip_code': '', 'department': None, 'department_id': None, 'department_name': None, 'end_date': None, 'file_upload_required': False, 'geofence': False, 'hour_budget': None, 'id': 9611835, 'latitude': None, 'logical_timestamp': 9113306981, 'longitude': None, 'name': 'Example 7', 'notes': 'these are my notes', 'number': '7', 'number_of_children': 0, 'parent': None, 'parent_name': None, 'permit_new_workreports': True, 'priority': None, 'remarks_required': None, 'resource_uri': '/web/v1/case/9611835/', 'responsible': None, 'responsible_id': None, 'responsible_name': None, 'responsibles': [], 'root_parent': None, 'start_date': None, 'street_address': '', 'uuid': None, 'zip_code': ''}]

#test processUpdates
# requires 1) Intempus account where data doesn't change, 2) Intempus account where data can be updated
# 3) sql scripts to set DB tables and data up in a test DB

#test readIntempus
# requires Intempus account where data doesn't change, if we want to verify data
def test_readIntempus():
    r, projects = main.readIntempus()
    assert r.ok is True
    assert type(projects) is dict 
    assert type(projects['objects']) is list
    assert type(projects['objects'][0]) is dict

# requires at least one record in the database to verify data types
def test_readDb():
    rv, projects = main.readDb()
    assert rv == 0 
    if type(projects) is list and len(projects) > 0:
        assert type(projects) is list 
        assert type(projects[0]) is dict

def input_to_db_update():
    with open("./data/params_updated_after_add.json", "r", encoding="utf-8") as jsonData:
        upd2Db = json.load(jsonData)
    return upd2Db

def test_genDbUpdate1():
    assert main.genDbUpdate(input_to_db_update()) == "UPDATE projects SET all_employees_may_add_work_reports=False, all_worktypes_may_used_in_work_reports=True, city='', country='', creation_date='2026-01-02', customer_city='', customer_country='DK', customer_name='Eksempelkunde', customer_street_address='Eksempelvej', customer_zip_code='', geofence=False, logical_timestamp=42, number_of_children=0, permit_new_workreports=True, resource_uri='/web/v1/case/9612054/', responsibles=ARRAY[]::VARCHAR[], street_address='', zip_code='' WHERE id=9612054"

def test_genDbUpdate2():
    assert main.genDbUpdate(input_to_db_update(), 1) == "UPDATE projects SET all_employees_may_add_work_reports=False, all_worktypes_may_used_in_work_reports=True, city='', country='', creation_date='2026-01-02', customer_city='', customer_country='DK', customer_name='Eksempelkunde', customer_street_address='Eksempelvej', customer_zip_code='', geofence=False, id=9612054, logical_timestamp=42, number_of_children=0, permit_new_workreports=True, resource_uri='/web/v1/case/9612054/', responsibles=ARRAY[]::VARCHAR[], street_address='', zip_code='' WHERE id=1"

def test_insertInDb():
    connection = shared.connectDb()
    cursor = connection.cursor()
    add2Db = input_to_db_update()
    add2Db['id'] = 100
    assert main.insertInDb(cursor, json.dumps(add2Db)) == 0
    #remove db entry
    shared.runSql(cursor, "DELETE FROM projects WHERE id=100;")
    connection.close()

def test_updateDb():
    connection = shared.connectDb()
    cursor = connection.cursor()
    add2Db = input_to_db_update()
    add2Db['id'] = 100
    main.insertInDb(cursor, json.dumps(add2Db)) == 0
    upd2Db = {
        'id': 100,
        'case_group': '{"company":"/web/v1/company/38167/","number":"2","name":"Project Group 2"}',
        'case_state': '{"company":"/web/v1/company/38167/","number":"2","name":"Project State 2"}',
        'department': '{"company":"/web/v1/company/38167/","number":"2","name":"Department 2"}'
    }
    assert main.updateDb(cursor, upd2Db) == 0
    #remove db entry
    shared.runSql(cursor, "DELETE FROM projects WHERE id=100;")
    connection.close()

# requires Intempus account where data doesn't change, if we want to verify data including id and resource_uri
def test_addToIntempus():
    connection = shared.connectDb()
    cursor = connection.cursor()

    with open("./data/payload_add.json", "r", encoding="utf-8") as jsonData:
        addObj = json.load(jsonData)
    #addObj = input_to_db_update()
    dbId = 100
    addObj["id"] = dbId
    addObj["name"] = "Example T1"
    addObj["number"] = "T1"

    rv = main.insertInDb(cursor, json.dumps(addObj))
    if not rv:
        rv = main.addToIntempus(cursor, addObj)
        assert rv == 0

        curdict = connection.cursor(cursor_factory=RealDictCursor)
        rv = shared.runSql(curdict, f"SELECT row_to_json(r) project FROM (SELECT * FROM {shared.MAIN_TABLE} WHERE number='T1') r;")
        if not rv:
            dbData = curdict.fetchall()
            if len(dbData):
                assert len(dbData) == 1
                for row in dbData:
                    assert row['project']['number'] == 'T1'
                    id = row['project']['id']

            assert id is not None
            url = f"https://intempus.dk/web/v1/case/{id}"
            apikey = os.environ['INTEMPUS_APIKEY']
            user = os.environ['INTEMPUS_USER']
            headers = {'authorization': f'apikey {user}:{apikey}', 'accept': 'application/json'}
            r = requests.delete(url, headers=headers)
            assert r.ok and r.status_code in (200, 204)
        
        shared.runSql(cursor, "DELETE FROM projects WHERE number='T1'")
    
    connection.close()


