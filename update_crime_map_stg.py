#--------------------------------
# Author: Erika Kamptner
# Description:  Upload latest_from_nypd to CARTO
#               Push to staging
# Created: 01/30/2017
# Log:
# 05/04/2017	modified email section
#--------------------------------

import requests, csv, time, json, win32com.client, os.path, re
from win32com.client import Dispatch, constants

file = "T:/GIS/Projects/DoITT/Crime Map 2.0/dataFromNYPD/latest_from_nypd.csv"
headers = ['BORO', 'PCT', 'SCT', 'MO', 'TYPE', 'LAT', 'LNG']

#API VARIABLES
account = input('Carto Account: ')
APIKey = input('API Key: ')
POSTendpoint = "https://"+account+".carto.com/api/v1/imports/"
SQLendpoint = "https://"+account+".carto.com/api/v2/sql?q="

#EMAIL VARIABLES
const = win32com.client.constants
olMailItem = 0x0
obj = win32com.client.Dispatch("Outlook.Application")
newMail = obj.CreateItem(olMailItem)
newMail.To = input('Email: ')

s = requests.Session()

if os.path.isfile(file):
    #READ HEADER FIELDS
    files = {'file': open(file)}
    
    with open(file, "rb") as f:
        reader = csv.reader(f)
        i = reader.next()
        rest = [row for row in reader]
        f.close()

    #POST TO CARTO ACCOUNT (IF HEADERS ARE CORRECT)
    if cmp(headers, i) == 0:
        r = requests.post(POSTendpoint + "?api_key=" + APIKey, files=files)
      
        data = json.loads(r.text)
        item_queue_id = data["item_queue_id"]
        success_status = data["success"]

        print(success_status)

        #GET STATUS OF IMPORT
        response = requests.get(POSTendpoint + item_queue_id + "?api_key=" + APIKey, timeout= 15)
        dataresponse = json.loads(response.text)
        
        time.sleep(120)
                
        #EXECUTE FUNCTIONS
        response = requests.get(SQLendpoint + "Select * from update_stg_crime_map()" + "&api_key=" + APIKey)
        json_data = json.loads(response.text)

        status = json_data['rows']
        status_parse = status[0]
        status_message = status_parse['update_stg_crime_map']       

        newMail.Subject = "CRIME MAP UPDATE on STAGING"
        newMail.Body = "Data on staging: " + status_message + "\n"+ "\n" + "Spot check staging before proceding with update: https://csgis-stg-prx.csc.nycnet/crime/ " + "\n" + "\n" + "Push to production: file:///T:/GIS/Projects/DoITT/Crime%20Map%202.0/Python%20Scripts/update_crime_map_prd.py" 
        newMail.Send() 

    else:
        print('Error: The latest_from_NYPD.csv does not have proper headers')
        newMail.Subject = "ERROR: CRIME MAP UPDATE"
        newMail.Body = "Error: latest_from_NYPD.csv does not have proper headers:\n"+" | "
        newMail.Send() 
else:
    print("no update for you")