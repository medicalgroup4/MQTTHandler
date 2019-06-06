# Message class Version 0.12
# Handy class for handling messages sent via the broker.
# 
# Can convert received messages into an instance of this class
# Can turn instances of this class into strings to send to the broker via MQTT
class Message:
    __DELIMITER = ';' # delimiter used in the message string
    __PARAM_AMT = 5 # amount of fields/parameters in the message

    # error messages:
    __ERROR_WRONG_FIELD_AMT = "Wrong amount of fields supplied to the from_string method in the Message class: 5 expected, %d given"
    __ERROR_TYPE_CONFLICT = "Could not convert message string to a message object because of a type conflict: \"%s\". Please refer to the documentation."

    # constructor function
    # id (int): message ID
    # patient_id (int): id of the patient who sent the message
    # severity (int): how serious is the message
    # location (string): where is the message sent from
    # message (string): actual message
    def __init__(self, id:int, patient_id:int, severity:int, location:str, message:str):
        strings_concatenated = location + message
        if self.__DELIMITER in strings_concatenated:
            raise ValueError("No '%s' allowed in messages" % self.__DELIMITER)
        
        self.id = id
        self.patient_id = patient_id
        self.severity = severity
        self.location = location
        self.message = message
    
    # constructor function to generate a Message from a string
    # message (string): string containing:
    #                       id (int): message ID
    #                       patient_id (int): id of the patient who sent the message
    #                       severity (int): how serious is the message
    #                       location (string): where is the message sent from
    #                       message (string): actual message
    #                   seperated by the delimiter configured in the __DELIMITER constant
    #
    #                   format:
    #                       [id];[patient_id];[severity];[location];[message]
    #                       where ';' is the delimiter configured in the __DELIMITER constant
    @classmethod
    def from_string(self, message:str) -> "Message":
        list = message.split(self.__DELIMITER)
        list_length = len(list)
        if list_length != self.__PARAM_AMT:
            raise Exception(self.__ERROR_WRONG_FIELD_AMT % list_length)
        
        try:
            id = int(list[0])
            patient_id = int(list[1])
            severity = int(list[2])
            location = list[3]
            msg = list[4]
        except ValueError as e:
            raise Exception(self.__ERROR_TYPE_CONFLICT % message) from e
        else:
            return Message(id, patient_id, severity, location, msg)

    @classmethod
    def is_str_message(self, string:str) -> bool:
        try:
            Message.from_string(string)
        except:
            return False
        else:
            return True

    # function to express this object as a string. Return format:
    # [id];[patient_id];[severity];[location];[message]
    # where ';' is the delimiter configured in the __DELIMITER constant
    def __str__(self) -> str:
        string = ""
        add_to_string = [self.id, self.patient_id, self.severity, self.location, self.message]
        for i in range(len(add_to_string)):
            string = string + str(add_to_string[i]) + self.__DELIMITER
        
        return string[:-1]  # return all but last character