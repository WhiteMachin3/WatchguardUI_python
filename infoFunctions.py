import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# - Watchguard UI Wireless Connected Devices via Python requests
# - Tested on Watchguard T20 / Local Management
# + cookieAuthParam must be in format {"session_id":cookie} as returned in auth
# + Can be changed easily to return the info in other ways (JSON, Python Object) instead of prints

def getWireless(ip, port, cookieAuthParam):
    try:
        url = "https://"+ip+":"+port+"/dashboard/dboard_get_system?report=wireless"
        headers = {"Accept": "application/json","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36", "Referer": "https://"+ip+":"+port+"/dashboard/system?report=wireless", "X-Requested-With": "XMLHttpRequest"}
        wirelessReq = requests.get(url, headers=headers, cookies=cookieAuthParam, verify=False)
        jsonResponse = json.loads(wirelessReq.text)
        # Remove the comment to see the full output of the json response 
        #print (jsonResponse)
        for x in jsonResponse["status"]["connected_users"]:
            print("MAC: "+x["mac"])
            if x["ip"]:
                print("IP: "+x["ip"])
            else:
                print("IP:")
            if x["host"]:
                print("HOSTNAME: "+x["host"])
            else:
                print("HOSTNAME:")
            print("////")
    except Exception as e:
        print (e)

