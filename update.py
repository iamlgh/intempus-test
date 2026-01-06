import json
import logging
import re
import requests
import os
import time    

logger = logging.getLogger(__name__)
logging.basicConfig(filename='update.log', encoding='utf-8', level=logging.DEBUG)

debug_requests = False
if debug_requests:
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARN)
    requests_log.propagate = True

with open("./data/data.json", "r") as file:
    data = json.load(file)

if data:
    dataType = "str"
    apikey = os.environ['INTEMPUS_APIKEY']
    user = os.environ['INTEMPUS_USER']
    headers = {'authorization': f'apikey {user}:{apikey}', 'accept': 'application/json', 'content-type': 'application/json'}

    # don't change id and resource_uri because they are what is being updated
    # don't change customer and customer_id, because I only have access to one customer
    # don't change parent or priority, because I see no way to add
    # dont change co_responsible, responsible, responsibles because employees probably need to be created separately, 
    # in order to set them as responsible. The result is always "You cannot specify pk when creating an instance" when
    # nesting the employee
    skipKeys = ('id', 'resource_uri', 'customer', 'customer_id', 'co_responsible', 'parent', 'priority', 'responsible', 'responsibles')
    
    for key in data.keys():
    #for key in ('responsible'):
        print(key)
        dType = type(data[key])
        value = data[key]

        numb = 12345
        
        if key in skipKeys:
            continue
        elif dType is str:
            print("str")
            if re.search("^\\d{4}-\\d{2}-\\d{2}$", value):
                #match date like 2025-12-22
                value = "2025-12-30"
            else:
                value += "a"
        elif data[key] is None:
            print("null")
            if re.search("_date$", key):
                #match _date key
                value = "2025-12-30"
            elif re.search("latitude$", key):
                value = 55.6238
            elif re.search("longitude$", key):
                value = 12.5942
            elif re.search("_id$", key):
                numb += 1
                value = str(numb)
            elif key == "hour_budget":
                value = 155.5
            elif key == "case_group":
                case_group = True
                if not case_group:
                    value = {"company":"/web/v1/company/38167/","number":"2","name":"Project Group 2"}
                else:
                    value = "/web/v1/case_group/16694/"
            elif key == "case_state":
                case_state = True
                if not case_state:
                    value = {"company":"/web/v1/company/38167/","number":"2","name":"Project State 2"}
                else:
                    value = "/web/v1/case_state/4131/"
            elif key == "department":
                department = True
                if not case_state:
                    value = {"company":"/web/v1/company/38167/","number":"2","name":"Department 2"}
                else:
                    value = "/web/v1/department/149056/"
            else:
                value = "a"
        elif dType is bool:
            print("bool")
            value = not value
            # always set geofence to false, maybe because there are no coordinates set?
            if key == "geofence":
                value = False
        elif dType is int:
            print("int")
            value += 5
        elif dType is float:
            print("float")
            if re.search("(latitude|longitude)$", key):
                value = 55.5 #must be between -90 and +90
            else:
                value += 5
        elif dType is list:
            print("list")
            value.append("a")
        else:
            break
        payload = {key: value}
        if key == "end_date": #needs a start date
            payload = {key: "2026-12-30", "start_date": "2025-12-30"}
        print(payload)
        logger.debug(payload)
        logger.debug(json.dumps)
        logger.debug(int(time.time()))
        url = f"https://intempus.dk{data['resource_uri']}"
        r = requests.put(url, headers=headers, data=json.dumps(payload))
        logger.debug(int(time.time()))
        logger.debug(r)
        logger.debug(r.text)
        logger.debug(r.reason)
        if r.ok:
            with open('./data/data2.json', 'w') as fp:
                json.dump(r.json(), fp)
        if r.status_code != 200:
            print(r)
            break
