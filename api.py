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

#Checks if Patient has middle name, returns FirstName + MiddleName + LastName as Name
def checkMiddleName(firstName, middleName, lastName):
    if middleName == None:
        name = str(firstName) + ' ' + str(lastName)
    else:
        name = str(firstName) + ' ' + str(middleName) + ' ' + str(lastName)
    return name

#Returns JSON of all patients
def showAllPatients():
    cursor = connection.cursor()
    cursor.execute(
        'SELECT FirstName, MiddleName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber FROM PATIENT;'
        )
    rows = cursor.fetchall()
    
    patientDict = dict()
    count = 0
    for row in rows:
        name = checkMiddleName(row[0], row[1], row[2])
        patientDict[count] = {'Name': name, 'Gender': row[3], 'DOB': row[4], 'Address': row[5], 'Phone': row[6], 'InsuranceNumber': row[7]}
        count += 1
    patientJson = json.dumps(patientDict)
    return patientJson

#find Patient in DB by insurance number or name
def findPatient(firstName, middleName, lastName, insuranceNum):
    cursor = connection.cursor()
    #if all parameters are empty, return all patients in DB
    if firstName == None and lastName == None and middleName == None and insuranceNum == None:
        return showAllPatients()
    #Search by insuranceNum if its present
    elif insuranceNum != None:
        cursor.execute(
        'SELECT FirstName, MiddleName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber FROM PATIENT WHERE InsuranceNumber = ?;', (int(insuranceNum), )
        )
    #if insuranceNum is not present, search other params
    elif insuranceNum == None:
        if middleName == None or middleName == 'None':
            cursor.execute(
            'SELECT FirstName, MiddleName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber FROM PATIENT WHERE FirstName = ? AND LastName = ?;', (str(firstName), str(lastName))
            )
        else:
            cursor.execute(
            'SELECT FirstName, MiddleName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber FROM PATIENT WHERE FirstName = ? AND MiddleName = ? AND LastName = ?;', (str(firstName), str(middleName), str(lastName))
            )     
    
    rows = cursor.fetchall()
    patientDict = dict()
    count = 0
    for row in rows:
        name = checkMiddleName(row[0], row[1], row[2])
        patientDict[count] = {'Name': name, 'Gender': row[3], 'DOB': row[4], 'Address': row[5], 'Phone': row[6], 'InsuranceNumber': row[7]}
        count += 1
    patientJson = json.dumps(patientDict)
    return patientJson



#Initialization of Flask's endpoints
# application = Flask(__name__)
#application.add_url_rule("/", "index", index)
#application.add_url_rule("/game/start/buyperiod", "startBuyPeriod", startBuyPeriod, methods = ["POST"])
#application.add_url_rule("/game/updatecoins", "updateCoins", updateCoins, methods = ["POST"])
    
# if __name__ == "__main__":
#     application.debug = True
#     application.run()