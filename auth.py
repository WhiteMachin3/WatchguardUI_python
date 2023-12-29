import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# - Watchguard UI Authentication via Python requests
# - Tested on Watchguard T20 / Local Management

#MODIFY THESE VARIABLES FOR TESTING PURPOSES
userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36"
ip = "127.0.0.1"
port = "8080"
passwd = "Root1234"
debug = True

def testConnection(ip):
    try:
        req = requests.get('https://'+ip+':'+port, verify=False, timeout=6)
        return True
    except:
        return False

#AUTH STEP BY STEP
def authLoginProcess(ip,port, passwd):

    if testConnection(ip) == False:
        if debug:print ("Watchguard WebUI missing in the current URL - https://"+ip+":"+port)
        sys.exit(1)

    #First Step - REQUEST INTO LOGIN ACCESS | GETTING SESSION COOKIE AND CP_CSRF_TOKEN 
    stepOne = requests.get('https://'+ip+':'+port+'/auth/login?from_page=/', verify=False)
    cookie = stepOne.headers.get("Set-Cookie").split(";")[0].split("=")[1]
    cp_csrf_token = stepOne.text.split("cp_csrf_token\" value=\"")[1].split("\"")[0]


    #Second Step - POST INTO AGENT/LOGIN VIA XML | GETTING SID AND WGA_CSRF_TOKEN | VERIFY IF LOGIN CREDS ARE VALID
    #Referer is a must
    #Hardcoded admin user as default, change if needed
    xmlData = "<methodCall><methodName>login</methodName><params><param><value><struct><member><name>password</name><value><string>"+passwd+"</string></value></member><member><name>user</name><value><string>admin</string></value></member><member><name>domain</name><value><string>Firebox-DB</string></value></member><member><name>uitype</name><value><string>2</string></value></member></struct></value></param></params></methodCall>"
    headers = {"Referer":"https://"+ip+":"+port+"/auth/login?from_page=/", "User-Agent":userAgent}
    cookies={'session_id':cookie}
    stepTwo = requests.post("https://"+ip+":"+port+"/agent/login", data=xmlData, cookies=cookies, headers=headers, verify=False)


    try:
        sid=stepTwo.text.split("<member><name>sid</name><value>")[1].split("</value>")[0]
        wga_csrf_token=stepTwo.text.split("<member><name>csrf_token</name><value>")[1].split("</value>")[0]

        #Third Step - POST INTO AUTH VIA PARAMS ON BODY | WE NEED TO USE BOTH CSRF TOKENS AND SID | IF LOGIN SUCCESFULLY, RETURN VALID AUTH COOKIE
        paramsLogin = {'username':'admin','password':passwd, 'domain':'Firebox-DB', 'sid':sid, 'wga_csrf_token':wga_csrf_token, 'cp_csrf_token':cp_csrf_token, 'privilege':2,'from_page':"%2F"}
        stepThree = requests.post("https://"+ip+":"+port+"/auth/login", data=paramsLogin, cookies=cookies, headers=headers, verify=False)
        if "Gateway Wireless Controller" in stepThree.text:
            rawHeadersAuth = stepThree.headers
            cookieAuth = str(rawHeadersAuth).split("\'Set-Cookie': \'session_id=")[1].split(";")[0]
            if debug:print("Logged in succesfully - Cookie: "+cookieAuth)
            return {"session_id":cookieAuth}

        else:
            if debug:print ("Error loading the interface after the login")
            sys.exit(1)
    except:
        if debug:print("Incorrect Password")
        sys.exit(1)

authLoginProcess(ip,port, passwd)
