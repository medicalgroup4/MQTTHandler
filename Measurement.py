# Measurement class
# Handy class for handling messages sent via the broker.
# 
# Can convert received messages into an instance of this class
# Can turn instances of this class into strings to send to the broker via MQTT
class Measurement:
    __DELIMITER = ';' # delimiter used in the message string
    __PARAM_AMT = 6 # amount of fields/parameters in the message

    # error messages:
    __ERROR_WRONG_FIELD_AMT = "Wrong amount of fields supplied to the from_string method in the Message class: %d expected, %d given"
    __ERROR_TYPE_CONFLICT = "Could not convert measurement string to a measurement object because of a type conflict: \"%s\". Please refer to the documentation."

    # constructor function
    # id (int): message ID
    # patient_id (int): id of the patient who sent did the measurement
    # systolic (float): measured systolic pressure
    # diastolic (float): measured diastolic pressure
    # oxygen (float): measured oxygen in blood
    # heartrate (float): measured heartrate
    def __init__(self, id:int, patient_id:int, systolic:float, diastolic:float, oxygen:float, heartrate:float):      
        self.id = id
        self.patient_id = patient_id
        self.systolic = systolic
        self.diastolic = diastolic
        self.oxygen = oxygen
        self.heartrate = heartrate
    
    # constructor function to generate a Measurement from a string
    # measurement (string): string containing:
    #                           id (int): message ID
    #                           patient_id (int): id of the patient who sent the measurement
    #                           systolic (float): measured systolic pressure
    #                           diastolic (float): measured diastolic pressure
    #                           oxygen (float): measured oxygen
    #                           heartrate (float): measured heartrate
    #                       seperated by the delimiter configured in the __DELIMITER constant
    #
    #                   format:
    #                       [id];[patient_id];[systolic];[diastolic];[oxygen];[heartrate]
    #                       where ';' is the delimiter configured in the __DELIMITER constant
    @classmethod
    def from_string(self, measurement:str) -> "Measurement":
        list = measurement.split(self.__DELIMITER)
        list_length = len(list)
        if list_length != self.__PARAM_AMT:
            raise Exception(self.__ERROR_WRONG_FIELD_AMT % (self.__PARAM_AMT, list_length))
        
        try:
            id = int(list[0])
            patient_id = int(list[1])
            systolic = float(list[2])
            diastolic = float(list[3])
            oxygen = float(list[4])
            heartrate = float(list[5])
        except ValueError as e:
            raise Exception(self.__ERROR_TYPE_CONFLICT % measurement) from e
        else:
            return Measurement(id, patient_id, systolic, diastolic, oxygen, heartrate)

    @classmethod
    def is_str_measurement(self, string:str) -> bool:
        try:
            Measurement.from_string(string)
        except:
            return False
        else:
            return True

    # function to express this object as a string. Return format:
    # [id];[patient_id];[systolic];[diastolic];[oxygen];[heartrate]
    # where ';' is the delimiter configured in the __DELIMITER constant
    def __str__(self) -> str:
        string = ""
        add_to_string = [self.id, self.patient_id, self.systolic, self.diastolic, self.oxygen, self.heartrate]
        for i in range(len(add_to_string)):
            string = string + str(add_to_string[i]) + self.__DELIMITER
        
        return string[:-1]  # return all but last character