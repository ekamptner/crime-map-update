#--------------------------------
# Author: Erika Kamptner
# Description:  Push to production
#               Remove file from temp folder
# Created: 01/30/2017
# Log:
# 05/04/2017	modified email section
#--------------------------------

import requests, win32com.client, os.path, re, shutil, json
from win32com.client import Dispatch, constants

#API VARIABLES
account = input('Carto Account: ')
APIKey = input('API Key: ')
SQLendpoint = "https://"+account+".carto.com/api/v2/sql?q="

#EMAIL VARIABLES
const = win32com.client.constants
olMailItem = 0x0
obj = win32com.client.Dispatch("Outlook.Application")
newMail = obj.CreateItem(olMailItem)
newMail.To = input('Email: ')

#REQUEST
response = requests.get(SQLendpoint + "Select * from update_prd_crime_map()" + "&api_key=" + APIKey)
json_data = json.loads(response.text)

status = json_data['rows']
status_parse = status[0]
status_message = status_parse['update_prd_crime_map']   

newMail.Subject = "Crime Map Update: Pushed to Production"
newMail.Body = "Update is complete. " + status_message + "\n"+ "\n" + "Verify data looks correct on production: https://maps.nyc.gov/crime/" 
newMail.Send()
