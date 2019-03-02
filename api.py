import sqlite3
from sqlite3 import Error
from flask import Flask, request, abort
import os
import json

#Setting up path to the current working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

database = 'hospitalDB.db'
connection = sqlite3.connect(database)


def showAllPatients():
    cursor = connection.cursor()
    cursor.execute(
        'SELECT FirstName, MiddleName, LastName, Gender, DateOfBirth AS DOB, Address, Phone, InsuranceNumber FROM PATIENT;'
        )
    rows = cursor.fetchall()
    
    patientDict = dict()
    count = 0
    for row in rows:
        if row[1] == None:
            name = str(row[0]) + ' ' + str(row[2])
        else:
            name = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[2])
        patientDict[count] = {'Name': name, 'Gender': row[3], 'DOB': row[4], 'Address': row[5], 'Phone': row[6], 'InsuranceNumber': row[7]}
        count += 1
    patientJson = json.dumps(patientDict)
    return patientJson


print(showAllPatients())
#Initialization of Flask's endpoints
# application = Flask(__name__)
#application.add_url_rule("/", "index", index)
#application.add_url_rule("/game/start/buyperiod", "startBuyPeriod", startBuyPeriod, methods = ["POST"])
#application.add_url_rule("/game/updatecoins", "updateCoins", updateCoins, methods = ["POST"])
    
# if __name__ == "__main__":
#     application.debug = True
#     application.run()