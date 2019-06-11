"""
topic for receiving message: message
topic for receiving measurement: measurement

topic for watch response: watch/ack
"""

from MQTT import *
from DbConnector import *

mqtt = MQTT(ip="51.83.42.157", port=1883, qos=2, mode=Message_mode.BLOCKING)

DB = DbConnector()

def database_message_callback(message):
    patient_name = DB.getPatientName(message.patient_id)
    print("Received message on topic message with id %d" % message.id)
    print("For patient with id %d and name %s" % (message.patient_id, patient_name))
    print("With severity %d" % message.severity)
    print("At location %s" % message.location)
    print("Message contents:\n%s" % message.message)
    DB.storeMessage(message)
    latest_message = DB.getLatestMessageFrom(message.patient_id)
    mqtt.publish_message("watch/message", latest_message)
    

def database_measurement_callback(measurement):
    print("received database measurement on topic measurement with id %d" % measurement.id)
    print("From patient with id %d" % measurement.patient_id)
    print("systolic pressure: %d" % measurement.systolic)
    print("diastolic pressure: %d" % measurement.diastolic)
    print("oxygen: %d" % measurement.oxygen)
    print("Heartrate: %d" % measurement.heartrate)
    DB.storeMeasurement(measurement)

def watch_confirm_message(message):
    if message.isdigit():
        id = int(message)
        DB.confirmMessage(id)

def message_callback(topic, message):
    topic_lookup = {
        "database/message": database_message_callback,
        "database/measurement": database_measurement_callback,
        "watch/confirm": watch_confirm_message
    }
    topic_lookup[topic](message)

mqtt.message_callback = message_callback
mqtt.sub_to_topics(["database/message", "database/measurement", "watch/confirm"])

try:
    mqtt.connect()
except KeyboardInterrupt:
    mqtt.disconnect()
    print("Bye!")