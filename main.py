"""
topic for receiving message: message
topic for receiving measurement: measurement

topic for watch response: watch/ack
"""

from MQTT import *
from DbConnector import *

TOPICS = {
    "MESSAGE_FROM_PATIENT": "database/message",
    "MEASUREMENT_FROM_PATIENT": "database/measurement",
    "NURSE_CONFIRMED_MESSAGE": "watch/confirm",
    "MESSAGE_FOR_WATCH": "watch/message",
    "NEW_WATCH_CONNECTED": "watch/connected",
}

ALARM_BOUNDARIES = {
    "SYSTOLIC_UPPER": 145,
    "SYSTOLIC_LOWER": 90,
    "HEARTRATE_LOWER": 50,
    "HEARTRATE_UPPER": 110,
    "OXYGEN_LOWER": 80
}


mqtt = MQTT(ip="51.83.42.157", port=1883, qos=2, mode=Message_mode.BLOCKING)

DB = DbConnector()

def database_message_callback(message):
    patient_info = DB.getPatientInfo(message.patient_id)

    if patient_info is None:
        print("Couldn't find patient with id " + message.patient_id)
        patient_name = "unknown"
    else:
        patient_name = patient_info[0]

    print("Received message on topic message with id %d" % message.id)
    print("For patient with id %d and name %s" % (message.patient_id, patient_name))
    print("With severity %d" % message.severity)
    print("At location %s" % message.location)
    print("Message contents:\n%s" % message.message)
    DB.storeMessage(message)
    latest_message = DB.getLatestMessageFrom(message.patient_id)
    mqtt.publish_message(TOPICS["MESSAGE_FOR_WATCH"], latest_message)
    

def database_measurement_callback(measurement):
    print("received database measurement on topic measurement with id %d" % measurement.id)
    print("From patient with id %d" % measurement.patient_id)
    print("systolic pressure: %d" % measurement.systolic)
    print("diastolic pressure: %d" % measurement.diastolic)
    print("oxygen: %d" % measurement.oxygen)
    print("Heartrate: %d" % measurement.heartrate)
    DB.storeMeasurement(measurement)
    checkForAlarms(measurement)

def checkForAlarms(measurement):
    systolicTooLow = measurement.systolic < ALARM_BOUNDARIES["SYSTOLIC_LOWER"]
    systolicTooHigh = measurement.systolic > ALARM_BOUNDARIES["SYSTOLIC_UPPER"]

    heartrateTooLow = measurement.heartrate < ALARM_BOUNDARIES["HEARTRATE_LOWER"]
    heartrateTooHigh = measurement.heartrate > ALARM_BOUNDARIES["HEARTRATE_UPPER"]

    systolicAlarm = systolicTooLow or systolicTooHigh
    heartrateAlarm = heartrateTooLow or heartrateTooHigh
    oxygenAlarm = measurement.oxygen < ALARM_BOUNDARIES["OXYGEN_LOWER"]

    if systolicAlarm or heartrateAlarm or oxygenAlarm:
        patient_info = DB.getPatientInfo(measurement.patient_id)
        patient_name = "unknown"
        patient_location = "unknown"
        if patient_info is not None:
            patient_name = patient_info[0]
            patient_location = patient_info[1]
    else:
        return

    if systolicAlarm:
        m = Message(0, measurement.patient_id, 2, patient_location,
                    "%s has a systolic pressure of %d" % (patient_name, measurement.systolic))
        mqtt.publish_message(TOPICS["MESSAGE_FOR_WATCH"], m)
    
    if heartrateAlarm:
        m = Message(0, measurement.patient_id, 2, patient_location,
                    "%s has a heartrate of %d" % (patient_name, measurement.heartrate))
        mqtt.publish_message(TOPICS["MESSAGE_FOR_WATCH"], m)
    
    if oxygenAlarm:
        m = Message(0, measurement.patient_id, 2, patient_location,
                    "%s has an oxygen percentage of %d" % (patient_name, measurement.oxygen))
        mqtt.publish_message(TOPICS["MESSAGE_FOR_WATCH"], m)


def watch_confirm_message(message):
    try:
        id = int(message)
        print("Confirming message %d" % id)
        DB.confirmMessage(id)
    except:
        print("message confirm ID was not an integer: %s" % message)

def watch_connected(message):
    unconfirmedMessages = DB.getUnconfirmedMessages()
    if unconfirmedMessages is not None:
        for message in unconfirmedMessages:
            mqtt.publish_message(TOPICS["MESSAGE_FOR_WATCH"], message)

def message_callback(topic, message):
    topic_lookup = {
        TOPICS["MESSAGE_FROM_PATIENT"]: database_message_callback,
        TOPICS["MEASUREMENT_FROM_PATIENT"]: database_measurement_callback,
        TOPICS["NURSE_CONFIRMED_MESSAGE"]: watch_confirm_message,
        TOPICS["NEW_WATCH_CONNECTED"]: watch_connected
    }
    topic_lookup[topic](message)

mqtt.message_callback = message_callback

mqtt.sub_to_topics([TOPICS["MESSAGE_FROM_PATIENT"],
                    TOPICS["MEASUREMENT_FROM_PATIENT"],
                    TOPICS["NURSE_CONFIRMED_MESSAGE"],
                    TOPICS["NEW_WATCH_CONNECTED"]])

try:
    mqtt.connect()
except KeyboardInterrupt:
    mqtt.disconnect()
    print("Bye!")