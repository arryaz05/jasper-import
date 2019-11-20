import argparse
import getpass
import urllib.request
import json
import time
import zipfile
import os
import shutil
import logging
import sys
from http.cookies import SimpleCookie

def cleanTemp():
    if os.path.exists('./temp_files'):
        shutil.rmtree('./temp_files')

# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-user')
parser.add_argument('-org')
parser.add_argument('-file')
parser.add_argument('-host')
args = parser.parse_args()
user = args.user
org = args.org if args.org != None else ''
importFile = args.file
host = args.host

# Logger
logging.basicConfig(filename= './' + importFile[:-4] + '.log',level=logging.DEBUG, format='%(asctime)s --> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Read Zip File 
try:
    with zipfile.ZipFile(importFile, 'r') as zip_f:
        zip_f.extractall('./temp_files')
except (zipfile.BadZipfile, zipfile.LargeZipFile) as e:
    logging.error('Error Unzipping file: ' + str(e))
    print('Error Unzipping file')
    cleanTemp()
    sys.exit()

# Authenticate with server and Get Cookie Token.
def Connect(host, org, user, pwd):
    try:
        cred = 'j_username=' + (user + '%7C' if org != '' else user) + '&j_password=' + pwd
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': 'userLocale=en'}
        conn = urllib.request.Request(method='GET', url= host + "rest_v2/login?" + cred, headers=headers )
        req = urllib.request.urlopen(conn)
        status = req.status
        if status == 200:
            print('Connected to: ' + host + "\n")
            #Get Response Session Id and save it in token variable for future use.
            #c = vars(req)['headers']['Set-Cookie']
            #cookie = SimpleCookie()
            return True
    except urllib.error.URLError as e:
        logging.error('Error Connecting to host: ' + str(e))
        print('Error connecting to host')
        cleanTemp()
        

# Query Job Status until succeed/fail
def CheckStatus(jobId):
    cred = 'j_username=' + (user + '%7C' if org != '' else user) + '&j_password=' + pwd
    headers = {'Accept': 'application/json'}
    finished = False
    while finished == False:
        try:
            req = urllib.request.Request(url= host + 'rest_v2/import/' + jobId + '/state?' + cred , method='GET', headers=headers)
            response = json.loads(urllib.request.urlopen(req).read().decode()) 
            if(response['phase'] == 'finished'):
                print(response['message'] )
                finished = True
            else:
                time.sleep(1)
        except urllib.error.URLError as e:
            logging.error('Error checking status for Job ' + jobId + ': ' + str(e))
            print('Error checking status for Job')
            cleanTemp()
            return False

# Send zip file to server to Start import.
def Import(name, import_file, host):
    cred = '&j_username=' + (user + '%7C' if org != '' else user) + '&j_password=' + pwd
    headers = {'Content-Type': 'application/zip', 'Accept': 'application/json'}
    arguments = 'update=true&skipUserUpdate=false&includeAccessEvents=true&includeServerSetting=true'
    try:
        req = urllib.request.Request(url= host + 'rest_v2/import?' + arguments + cred , method='POST', headers=headers, data=import_file)
        response = json.loads(urllib.request.urlopen(req).read().decode()) 
        if response['phase'] == 'inprogress':
            print(response['message'], '[' + name + ']')
            print('Job ID: ', response['id'])
            CheckStatus(response['id'])
        else:
            print(response['message'])
    except urllib.error.URLError as e:
        logging.error('Error Importing file to host: ' + str(e))
        print('Error Importing file to host')
        cleanTemp()
        return False


# Ask For Password
pwd = getpass.getpass('Insert Password for ' + user + ': ')

# Attempt Connection
if Connect(host, org, user, pwd) == True:

    #Show Release Note
    try:
        with open('./temp_files/release_note.txt') as myfile:
            release_note = myfile.read()
            print('[Release Note]')
            print(release_note)
    except:
        print('WARNING: No release note found.')

    # Select Operation
    input_op = 3
    while input_op not in ['1','2']:
        print('Select Operation for ' + importFile + ": ")
        print('[1] Install')
        print('[2] Uninstall')
        input_op = input()
        print('')
    op = 'Install' if input_op == '1' else 'Uninstall'
    folder_dir = './temp_files/' + op + '/'
    try:
        packages = os.listdir(folder_dir)
    except:
        logging.error('Error: Operation Package not found.')
        print('Error')
        cleanTemp()


    # Start Import
    if len(packages) == 0:
        logging.error('Error: Operation Package is empty')
        print('Error')
        cleanTemp()
    else:
        for package in packages:
            zip_file = open(folder_dir + package  , 'rb').read()
            Import(package, zip_file, host)


# Clean Temporal Files
cleanTemp()
