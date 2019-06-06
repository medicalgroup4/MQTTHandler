import mysql.connector
from Message import Message


class DbConnector:
    @classmethod
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="1234Hoedjevan!",
            database="medicaldb"
        )
        print(self.mydb)

    # funciton that takes an instance of type Message and stores the data into the database
    def storeMessage(self, mes):
        mycursor = self.mydb.cursor()

        sql = "INSERT INTO Messages (patient_id, severity, message, location) VALUES (%d, %d, %s, %s)"
        val = (mes.patient_id, mes.severity, mes.message, mes.location)
        mycursor.execute(sql, val)
        self.mydb.commit()
        print("Message inserted: ", val)

    # funciton that takes an instance of type Measurement and stores the data into the database
    def storeMeasurement(self, mea):
        mycursor = self.mydb.cursor()

        sql = "INSERT INTO Measurements (patient_id, systolic, diastolic, oxygen, heartrate) VALUES (%d, %f, %f, %f, %f)"
        val = (mea.patient_id, mea.systolic, mea.diastolic, mea.oxygen, mea.heartrate)
        mycursor.execute(sql, val)
        self.mydb.commit()
        print("Measurement inserted into db: ", val)




