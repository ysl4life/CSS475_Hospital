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
        'SELECT Patient.FirstName, Patient.MiddleName, Patient.LastName, Gender, DateOfBirth, Patient.Address, Patient.Phone, InsuranceNumber, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM PATIENT, DOCTOR WHERE Patient.DoctorID = Doctor.ID;'
        )
    rows = cursor.fetchall()
    
    patientDict = dict()
    count = 0
    for row in rows:
        name = checkMiddleName(row[0], row[1], row[2])
        patientDict[count] = {'Name': name, 'Gender': row[3], 'DOB': row[4], 'Address': row[5], 'Phone': row[6], 'InsuranceNumber': row[7], 'PrimaryDoctor': row[8]}
        count += 1
    patientJson = json.dumps(patientDict)
    return patientJson

#find Patient in DB by insurance number or name. If no input = return all patients
def findPatient(firstName, middleName, lastName, insuranceNum):
    cursor = connection.cursor()
    #if all parameters are empty, return all patients in DB
    if firstName == None and lastName == None and middleName == None and insuranceNum == None:
        return showAllPatients()
    #Search by insuranceNum if its present
    elif insuranceNum != None:
        cursor.execute(
        'SELECT Patient.FirstName, Patient.MiddleName, Patient.LastName, Gender, DateOfBirth, Patient.Address, Patient.Phone, InsuranceNumber, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM PATIENT, DOCTOR WHERE InsuranceNumber = ? AND Patient.DoctorID = Doctor.ID;', (int(insuranceNum), )
        )
    #if insuranceNum is not present, search other params
    elif insuranceNum == None:
        if middleName == None or middleName == 'None':
            cursor.execute(
            'SELECT Patient.FirstName, Patient.MiddleName, Patient.LastName, Gender, DateOfBirth, Patient.Address, Patient.Phone, InsuranceNumber, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM PATIENT, DOCTOR WHERE FirstName = ? AND LastName = ? AND Patient.DoctorID = Doctor.ID;', (str(firstName), str(lastName))
            )
        else:
            cursor.execute(
            'SELECT Patient.FirstName, Patient.MiddleName, Patient.LastName, Gender, DateOfBirth, Patient.Address, Patient.Phone, InsuranceNumber, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM PATIENT, DOCTOR WHERE FirstName = ? AND MiddleName = ? AND LastName = ? AND Patient.DoctorID = Doctor.ID;', (str(firstName), str(middleName), str(lastName))
            )     

    rows = cursor.fetchall()
    patientDict = dict()
    count = 0
    for row in rows:
        name = checkMiddleName(row[0], row[1], row[2])
        patientDict[count] = {'Name': name, 'Gender': row[3], 'DOB': row[4], 'Address': row[5], 'Phone': row[6], 'InsuranceNumber': row[7], 'PrimaryDoctor': row[8]}
        count += 1
    patientJson = json.dumps(patientDict)
    return patientJson

#returns info about patient's diagnoses
def getDiagnosis(insuranceNum):
    cursor = connection.cursor()
    cursor.execute('SELECT Diagnosis.ConditionName, PATIENTS_DIAGNOSES.DiagnosisDate, PATIENTS_DIAGNOSES.Remarks FROM PATIENT, PATIENTS_DIAGNOSES, DIAGNOSIS WHERE Patient.insurancenumber = ? AND Diagnosis.id = Patients_Diagnoses.DiagnosisID AND PAtients_Diagnoses.PatientID = Patient.ID;', (int(insuranceNum), )
    )
    rows = cursor.fetchall()
    diagnosisDict = dict()
    for row in rows:
        diagnosisDict['Diagnoses'] = {row[0]: {'Diagnosed on': row[1], 'Remarks': row[2]}}
    return diagnosisDict

#returns prescribed medication
def getPrescription(insuranceNum):
    cursor = connection.cursor()
    cursor.execute('SELECT Medication.name, Prescription.PrescribedAmount, Medication.MaxDosage, Prescription.Refill FROM Patient, Prescription, Medication WHERE Patient.insurancenumber = ? AND Medication.id = Prescription.medicationID AND Patient.id = Prescription.patientID;', (int(insuranceNum), ))
    rows = cursor.fetchall()
    prescriptionsDict = dict()
    for row in rows:
        if int(row[3]) == 1:
            refill = 'Yes'
        else:
            refill = 'No'
        prescriptionsDict['PrescribedMedication'] = {row[0]: {'PrescribedAmount': row[1], 'MaxDosage': row[2], 'Refill': refill}}
    return prescriptionsDict

#returns appointments
def getAppointments(insuranceNum):
    cursor = connection.cursor()
    cursor.execute('SELECT Appointment.StartTime, Duration, Description, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM Patient, Appointment, Doctor, APPOINTMENT_DOCTORS WHERE Patient.id = Appointment.PatientID AND Appointment.ID = APPOINTMENT_DOCTORS.AppointmentID AND Doctor.id = Appointment_Doctors.doctorID AND Patient.insurancenumber = ?;', (int(insuranceNum), ))
    rows = cursor.fetchall()
    appointmentDict = dict()
    for row in rows:
        appointmentDict['Appointments'] = {row[0]: {'Duration': row[1], 'Description': row[2], 'Doctor': row[3]}}
    return appointmentDict

#returns all data associated with patient
def getPatientInfo(insuranceNum):
    diagnoses = getDiagnosis(insuranceNum)
    prescription = getPrescription(insuranceNum)
    appointments = getAppointments(insuranceNum)
    patientInfoDict = {**diagnoses, **prescription, **appointments}
    patientInfoJson = json.dumps(patientInfoDict)
    return patientInfoJson

#print(getPatientInfo(111000111))
print(showAllPatients())

#Initialization of Flask's endpoints
# application = Flask(__name__)
#application.add_url_rule("/", "index", index)
#application.add_url_rule("/game/start/buyperiod", "startBuyPeriod", startBuyPeriod, methods = ["POST"])
#application.add_url_rule("/game/updatecoins", "updateCoins", updateCoins, methods = ["POST"])
    
# if __name__ == "__main__":
#     application.debug = True
#     application.run()