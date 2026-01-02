import json
import logging
import re
import requests
import os
import time    

logger = logging.getLogger(__name__)

debug = False
if debug:
    logging.basicConfig(filename='update.log', encoding='utf-8', level=logging.DEBUG)

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

    # don't change id and resource_uri because they are what is being updated
    # don't change customer and customer_id, because I only have access to one customer
    # don't change parent or priority, because I see no way to add
    # dont change co_responsible, responsible, responsibles because employees probably need to be created, in order to set them as responsible
    skipKeys = ('id', 'resource_uri', 'customer', 'customer_id', 'co_responsible', 'parent', 'priority', 'responsible', 'responsibles')

    url = f"https://intempus.dk{data['resource_uri']}"
    apikey = os.environ['INTEMPUS_APIKEY']
    user = os.environ['INTEMPUS_USER']
    headers = {'authorization': f'apikey {user}:{apikey}', 'accept': 'application/json', 'content-type': 'application/json'}
    for key in data.keys():
    #for key in ['department']:
        print(key)
        classedDataType = type(data[key])
        dataType = re.findall("'[^']+'", str(classedDataType))
        dataType = dataType[0].strip("'")
        value = data[key]

        numb = 12345
        
        if key in skipKeys:
            continue
        elif dataType == "str":
            if re.search("^\\d{4}-\\d{2}-\\d{2}$", value):
                #match date like 2025-12-22
                value = "2025-12-30"
            else:
                value += "a"
        elif dataType == "NoneType":
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
                #value = {"company":"/web/v1/company/38167/","number":"2","name":"Project Group 2"}
                value = "/web/v1/case_group/16694/"
            elif key == "case_state":
                #value = {"company":"/web/v1/company/38167/","number":"2","name":"Project State 2"}
                value = "/web/v1/case_state/4131/"
            elif key == "department":
                #value = {"company":"/web/v1/company/38167/","number":"2","name":"Department 2"}
                value = "/web/v1/department/149056/"
            else:
                value = "a"
        elif dataType == "bool":
            value = not value
            # always set geofence to false, maybe because there are no coordinates set?
            if key == "geofence":
                value = False
        elif dataType == "int":
            value += 5
        elif dataType == "float":
            if re.search("(latitude|longitude)$", key):
                value = 55.5 #must be between -90 and +90
            else:
                value += 5
        elif dataType == "list":
            value.append("a")
        else:
            break
        payload = {key: value}
        if key == "end_date": #needs a start date
            payload = {key: "2026-12-30", "start_date": "2025-12-30"}
        print(payload, f"({dataType})")
        logger.debug(payload)
        logger.debug(json.dumps)
        logger.debug(int(time.time()))
        r = requests.put(url, headers=headers, data=json.dumps(payload))
        logger.debug(int(time.time()))
        logger.debug(r)
        logger.debug(r.text)
        if r.status_code != 200:
            print(r)
            break
