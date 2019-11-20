import argparse
import getpass
import urllib.request
import json
import time
from http.cookies import SimpleCookie


# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-user")
parser.add_argument("-org")
parser.add_argument("-file")
args = parser.parse_args()
user = args.user
org = args.org if args.org != None else ''
importFile = args.file

# Host, Token & Read Zip File
host = 'http://jasper.samqua.com:8082/jasperserver/'        # <-- Change to target host...
token = None
zip_file = open(importFile  , 'rb').read()


# Authenticate with server and Get Cookie Token.
def Connect(host, org, user, pwd):
    global token
    try:
        cred = {'j_username': (user + '%7C' if org != '' else user), 'j_password': pwd}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        conn = urllib.request.Request(method='POST', url= host + "rest_v2/login", headers=headers, data= urllib.parse.urlencode(cred).encode() )
        req = urllib.request.urlopen(conn)
        status = req.status
        if status == 200:
            print('Connected to: ' + host + "\n")
            #Get Response Session Id and save it in config for future use
            c = vars(req)['headers']['Set-Cookie']
            cookie = SimpleCookie()
            cookie.load(c)
            token = cookie['JSESSIONID'].value
            return True
    except urllib.error.URLError as e:
        print(e)
        if hasattr(e, 'status'):
            return e.status
        else:
            return 'hosterror'

# Send zip file to server to Start import.
def Import(import_file, host, token):
    headers = {'Cookie': 'JSESSIONID=' + token, 'Content-Type': 'application/zip', 'Accept': 'application/json'}
    try:
        req = urllib.request.Request(url= host + 'rest_v2/import?update=true' , method='POST', headers=headers, data=import_file)
        response = json.loads(urllib.request.urlopen(req).read().decode()) 
        if response['phase'] == 'inprogress':
            print('Import Started')
            print('Job ID: ', response['id'])
            CheckStatus(response['id'])
        else:
            print(response['message'])
    except urllib.error.URLError as e:
        print(e)
        return False

def CheckStatus(id):
    headers = {'Cookie': 'JSESSIONID=' + token, 'Accept': 'application/json'}
    finished = False
    while finished == False:
        try:
            req = urllib.request.Request(url= host + 'rest_v2/import/' + id + '/state' , method='GET', headers=headers)
            response = json.loads(urllib.request.urlopen(req).read().decode()) 
            if(response['phase'] == 'finished'):
                print('Export Finished Succesfully')
                finished = True
            else:
                print(response['message'])
                time.sleep(5)
        except urllib.error.URLError as e:
            print(e)
            return False

# Ask For Password
pwd = getpass.getpass('Insert Password for ' + user + ': ')

# Attempt Connection
Connect(host, org, user, pwd)

# Import Target Zip File
Import(zip_file, host, token)





