import mysql.connector
from Message import Message

class DbConnector:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="51.83.42.157",
            user="remote",
            passwd="1234Hoedjevan!",
            database="medicaldb"
        )
        print(self.db)

    # function that takes an instance of type Message and stores the data into the database
    def storeMessage(self, mes):
        cursor = self.db.cursor()

        sql = "INSERT INTO Messages (patient_id, severity, message, location) VALUES (%s, %s, %s, %s)"
        val = (mes.patient_id, mes.severity, mes.message, mes.location)
        cursor.execute(sql, val)
        self.db.commit()
        print("Message inserted: ", val)
        cursor.close()
    
    def getLatestMessageFrom(self, patient_id):
        cursor = self.db.cursor(buffered=True)

        sql = "SELECT id, patient_id, severity, message, location FROM Messages WHERE patient_id = %s ORDER BY id DESC LIMIT 1"
        val = (patient_id,)
        cursor.execute(sql, val)
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        else:
            #               id            severity         message
            #                    patient_id       location
            return Message(row[0], row[1], row[2], row[4], row[3])


    # function that takes an instance of type Measurement and stores the data into the database
    def storeMeasurement(self, mea):
        cursor = self.db.cursor()

        sql = "INSERT INTO Measurements (patient_id, systolic, diastolic, oxygen, heartrate) VALUES (%s, %s, %s, %s, %s)"
        val = (mea.patient_id, mea.systolic, mea.diastolic, mea.oxygen, mea.heartrate)
        cursor.execute(sql, val)
        self.db.commit()
        cursor.close()
        print("Measurement inserted into db: ", val)
    

    def getPatientName(self, patient_id):
        cursor = self.db.cursor(buffered=True)
        sql = "SELECT name FROM Patients WHERE id = %s"
        val = (patient_id,)
        cursor.execute(sql, val)
        self.db.commit()
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        else:
            return row[0]

    def confirmMessage(self, message_id):
        cursor = self.db.cursor()
        sql = "UPDATE Messages SET confirmed = 1 WHERE id = %s;";
        val = (message_id,)
        cursor.execute(sql, val)
        self.db.commit()
        cursor.close()



