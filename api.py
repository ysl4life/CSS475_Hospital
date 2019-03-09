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

#app = Flask(__name__) #initialize Flask app

#Checks if Patient has middle name, returns FirstName + MiddleName + LastName as Name
def checkMiddleName(firstName, middleName, lastName):
    if middleName == None:
        name = str(firstName) + ' ' + str(lastName)
    else:
        name = str(firstName) + ' ' + str(middleName) + ' ' + str(lastName)
    return name

#Returns JSON of all patients
def showAllPatients():
    with sqlite3.connect(database) as connection:
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
        connection.commit()
    return patientJson

#find Patient in DB by insurance number or name. If no input = return all patients
#@app.route('/findPatient/<firstName>/<middleName>/<lastName>/<insuranceNum>')
def findPatient(firstName, middleName, lastName, insuranceNum):
    if firstName == 'None': firstName = None
    if lastName == 'None': lastName = None
    if middleName == 'None': middleName = None
    if insuranceNum == 'None': insuranceNum = None
    
    with sqlite3.connect(database) as connection:
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
            if middleName == None:
                cursor.execute(
                'SELECT Patient.FirstName, Patient.MiddleName, Patient.LastName, Gender, DateOfBirth, Patient.Address, Patient.Phone, InsuranceNumber, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM PATIENT, DOCTOR WHERE Patient.FirstName = ? AND Patient.LastName = ? AND Patient.DoctorID = Doctor.ID;', (str(firstName), str(lastName))
                )
            else:
                cursor.execute(
                'SELECT Patient.FirstName, Patient.MiddleName, Patient.LastName, Gender, DateOfBirth, Patient.Address, Patient.Phone, InsuranceNumber, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM PATIENT, DOCTOR WHERE Patient.FirstName = ? AND Patient.MiddleName = ? AND Patient.LastName = ? AND Patient.DoctorID = Doctor.ID;', (str(firstName), str(middleName), str(lastName))
                )     

        rows = cursor.fetchall()
        patientDict = dict()
        count = 0
        for row in rows:
            name = checkMiddleName(row[0], row[1], row[2])
            patientDict[count] = {'Name': name, 'Gender': row[3], 'DOB': row[4], 'Address': row[5], 'Phone': row[6], 'InsuranceNumber': row[7], 'PrimaryDoctor': row[8]}
            count += 1
        patientJson = json.dumps(patientDict)
        connection.commit()
    return patientJson

#returns info about patient's diagnoses
def getDiagnosis(insuranceNum):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT Diagnosis.ConditionName, PATIENTS_DIAGNOSES.DiagnosisDate, PATIENTS_DIAGNOSES.Remarks FROM PATIENT, PATIENTS_DIAGNOSES, DIAGNOSIS WHERE Patient.insurancenumber = ? AND Diagnosis.id = Patients_Diagnoses.DiagnosisID AND PAtients_Diagnoses.PatientID = Patient.ID;', (int(insuranceNum), )
        )
        rows = cursor.fetchall()
        diagnosisDict = dict()
        for row in rows:
            diagnosisDict['Diagnoses'] = {row[0]: {'Diagnosed on': row[1], 'Remarks': row[2]}}
        connection.commit()
    return diagnosisDict

#returns prescribed medication
def getPrescription(insuranceNum):
    with sqlite3.connect(database) as connection:
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
        connection.commit()
    return prescriptionsDict

#returns appointments for specific patient
def getAppointments(insuranceNum):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT Appointment.StartTime, Duration, Description, (Doctor.FirstName || " " || Doctor.LastName) as Doctor FROM Patient, Appointment, Doctor, APPOINTMENT_DOCTORS WHERE Patient.id = Appointment.PatientID AND Appointment.ID = APPOINTMENT_DOCTORS.AppointmentID AND Doctor.id = Appointment_Doctors.doctorID AND Patient.insurancenumber = ?;', (int(insuranceNum), ))
        rows = cursor.fetchall()
        appointmentDict = dict()
        for row in rows:
            appointmentDict['Appointments'] = {row[0]: {'Duration': row[1], 'Description': row[2], 'Doctor': row[3]}}
        connection.commit()
    return appointmentDict

#returns all data associated with patient
#@app.route('/getPatientInfo/<insuranceNum>')
def getPatientInfo(insuranceNum):
    diagnoses = getDiagnosis(insuranceNum)
    prescription = getPrescription(insuranceNum)
    appointments = getAppointments(insuranceNum)
    patientInfoDict = {**diagnoses, **prescription, **appointments}
    patientInfoJson = json.dumps(patientInfoDict)
    return patientInfoJson

#If the Patients exists in the DB return True, if doesn't exist return False
def doesPatientExist(insuranceNum):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT count(*) FROM PATIENT WHERE InsuranceNumber = ?;', (int(insuranceNum), ))
        rows = cursor.fetchall()
        if int(rows[0][0]) == 0:
            return False
        else:
            return True

#adds a new patient to the DB
#@app.route('/addPatient/<firstName>/<middleName>/<lastName>/<gender>/<DOB>/<address>/<phone>/<insuranceNum>', methods = ['POST'])
def addPatient(firstName, middleName, lastName, gender, DOB, address, phone, insuranceNum):
    doctorID = 1
    officeID = 1
   
    if middleName == 'None': middleName = None
    
    if doesPatientExist(insuranceNum) == False: #check if the patient doesn't exist in the DB
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            if middleName != None:
                cursor.execute('INSERT INTO Patient (DoctorID, FirstName, MiddleName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber, OfficeID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (doctorID, firstName, middleName, lastName, gender, DOB, address, phone, insuranceNum, officeID))
                connection.commit()
                return True
            else:
                cursor.execute('INSERT INTO Patient (DoctorID, FirstName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber, OfficeID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);', (doctorID, firstName, lastName, gender, DOB, address, phone, insuranceNum, officeID))
                connection.commit()
                return True
    else:
        return False

#removes patient from the database
#@app.route('/removePatient/<insuranceNum>', methods = ['POST'])
def removePatient(insuranceNum):
    if doesPatientExist(insuranceNum) == True: #check if the patient exists in the DB
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM PATIENT WHERE InsuranceNumber = ?;', (int(insuranceNum), ))
            connection.commit()
            return True
    else:
        return False

#updates general info of patient.
#@app.route('/updatePatient/<firstName>/<middleName>/<lastName>/<gender>/<address>/<phone>/<newInsuranceNum>/<oldInsuranceNum>', methods = ['POST'])
def updatePatient(firstName, middleName, lastName, gender, DOB, address, phone, newInsuranceNum, oldInsuranceNum):
    if firstName == 'None': firstName = None
    if middleName == 'None': middleName = None
    if lastName == 'None': lastName = None
    if gender == 'None': gender = None
    if DOB == 'None': DOB = None
    if address == 'None': address = None
    if phone == 'None': phone = None
    if newInsuranceNum == 'None': newInsuranceNum = None
    if doesPatientExist(oldInsuranceNum) == True:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            if firstName != None:
                cursor.execute('UPDATE Patient SET FirstName = ? WHERE InsuranceNumber = ?;', (str(firstName), int(oldInsuranceNum)))
            if middleName != None:
                cursor.execute('UPDATE Patient SET MiddleName = ? WHERE InsuranceNumber = ?;', (str(middleName), int(oldInsuranceNum)))
            if lastName != None:
                cursor.execute('UPDATE Patient SET LastName = ? WHERE InsuranceNumber = ?;', (str(lastName), int(oldInsuranceNum)))
            if gender != None:
                cursor.execute('UPDATE Patient SET gender = ? WHERE InsuranceNumber = ?;', (str(gender), int(oldInsuranceNum)))
            if DOB != None:
                cursor.execute('UPDATE Patient SET DateOfBirth = ? WHERE InsuranceNumber = ?;', (str(DOB), int(oldInsuranceNum)))
            if address != None:
                cursor.execute('UPDATE Patient SET address = ? WHERE InsuranceNumber = ?;', (str(address), int(oldInsuranceNum)))
            if phone != None:
                cursor.execute('UPDATE Patient SET phone = ? WHERE InsuranceNumber = ?;', (str(phone), int(oldInsuranceNum)))
            if newInsuranceNum != None:
                cursor.execute('UPDATE Patient SET InsuranceNumber = ? WHERE InsuranceNumber = ?;', (str(newInsuranceNum), int(oldInsuranceNum)))
            connection.commit()
            return True
    else:
        return False
    
#Returns all appointments that have not been done up to this point yet
#@app.route(/getAppointments/<upcomingOnly>')
def getAllAppointments(upcomingOnly):
    if upcomingOnly == 'None': upcomingOnly = None
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        if upcomingOnly == None: #if upcomingOnly == None, show all appointments
            cursor.execute('SELECT StartTime, Duration, Description, RoomNumber FROM Appointment, Room WHERE Appointment.RoomID = Room.ID ORDER BY StartTime ASC;')
        else: #if upcomingOnly != None, show only future appointments
            cursor.execute('SELECT StartTime, Duration, Description, RoomNumber FROM Appointment, Room WHERE Appointment.RoomID = Room.ID AND datetime(?) < Appointment.StartTime ORDER BY StartTime ASC;', ('now', ))
        rows = cursor.fetchall()
        appointmentDict = dict()
        for row in rows:
            appointmentDict[row[0]] = {'Duration': row[1], 'Description': row[2], 'RoomNumber': row[3]}
        appointmentsJson = json.dumps(appointmentDict)
    return appointmentsJson

#Verifies if Appointment exists by time
def doesAppointmentExist(startTime):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT count(*) FROM Appointment WHERE StartTime = ?;', (str(startTime), ))
        rows = cursor.fetchall()
        if int(rows[0][0]) == 0:
            return False
        else:
            return True

#Updates appointment's description and roomNumber
#@app.route(/updateAppointment/<time>/<description>/<roomNumber>', methods = ['POST'])
def updateAppointment(startTime, description, roomNumber):
    if description == 'None': description = None
    if roomNumber == 'None': roomNumber = None
    
    if doesAppointmentExist(startTime) == True:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            if description != None:
                cursor.execute('UPDATE Appointment SET Description = ? WHERE StartTime = ?;', (str(description), str(startTime)))
            if roomNumber != None:
                if roomNumber == '101':
                    roomID = 1
                if roomNumber == '102':
                    roomID = 2
                cursor.execute('UPDATE Appointment SET RoomID = ? WHERE StartTime = ?;', (str(roomID), str(startTime)))
            connection.commit()
            return True
    return False

#if time slot is occupied, returns True, if not occupied, returns False
def isTimeOccupied(startTime, duration):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('''SELECT count(*) FROM Appointment WHERE (StartTime <= ? AND datetime(StartTime, '+' ||duration|| ' minutes') >= ?) OR (StartTime <= datetime(?, '+' ||?|| ' minutes') AND datetime(StartTime, '+' ||duration|| ' minutes') >= datetime(?, '+' ||?|| ' minutes'));''', (str(startTime), str(startTime), str(startTime), str(duration), str(startTime), str(duration)))
        rows = cursor.fetchall()
        if int(rows[0][0]) == 0:
             return False
        else:
             return True

#Adds appointment to the DB
#@app.route(/addAppointment/<patientID/<roomNumber>/<startTime>/<duration>/<description>', methods = ['POST'])
def addAppointment(patientID, roomNumber, startTime, duration, description):
    if isTimeOccupied(startTime, duration) == False:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO Appointment (PatientID, RoomID, StartTime, Duration, Description) VALUES (?, ?, ?, ?, ?);', (patientID, roomNumber[2], startTime, duration, description))
            cursor.execute('INSERT INTO Appointment_Doctors (DoctorID, AppointmentID) VALUES (?, last_rowid());', (1, ))
            return True
    return False



# def addPatient(firstName, middleName, lastName, gender, DOB, address, phone, insuranceNum):
#     doctorID = 1
#     officeID = 1
   
#     if middleName == 'None': middleName = None
    
#     if doesPatientExist(insuranceNum) == False: #check if the patient doesn't exist in the DB
#         with sqlite3.connect(database) as connection:
#             cursor = connection.cursor()
#             if middleName != None:
#                 cursor.execute('INSERT INTO Patient (DoctorID, FirstName, MiddleName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber, OfficeID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (doctorID, firstName, middleName, lastName, gender, DOB, address, phone, insuranceNum, officeID))
#                 connection.commit()
#                 return True
#             else:
#                 cursor.execute('INSERT INTO Patient (DoctorID, FirstName, LastName, Gender, DateOfBirth, Address, Phone, InsuranceNumber, OfficeID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);', (doctorID, firstName, lastName, gender, DOB, address, phone, insuranceNum, officeID))
#                 connection.commit()
#                 return True
#     else:
#         return False

#Done:
# Show all patients in the DB
# Search for specific patient and return general info (from Patient table)
# Show prescribed medication, diagnoses, appoitnments of specific patient
# Add patient to the database
# Remove patient from the database
# Update Patient's info
# SHOW ALL APPOINTMENTS IN THE DB
# Update Appointment
#TO DO:
# ADD APPOINTMENT
# REMOVE APPOINTMENT

# if __name__ == "__main__":
#     app.debug = True
#     app.run()