"""
topic for receiving message: database/message
topic for receiving measurement: database/measurement

topic for sending message to watch: watch/message
topic for watch response: watch/ack
"""

from MQTT import *
from DbConnector import *

DB = DbConnector()

def database_message_callback(message):
    print("Received message on topic database/message with id %d" % message.id)
    print("For patient with id %d" % message.patient_id)
    print("With severity %d" % message.severity)
    print("At location %s" % message.location)
    print("Message contents:\n%s" % message.message)
    DB.storeMessage(message)
    

def database_measurement_callback(measurement):
    print("received database measurement on topic database/measurement with id %d" % measurement.id)
    print("From patient with id %d" % measurement.patient_id)
    print("systolic pressure: %d" % measurement.systolic)
    print("diastolic pressure: %d" % measurement.diastolic)
    print("oxygen: %d" % measurement.oxygen)
    print("Heartrate: %d" % measurement.heartrate)
    DB.storeMeasurement(measurement)

def message_callback(topic, message):
    topic_lookup = {
        "database/message": database_message_callback,
        "database/measurement": database_measurement_callback
    }
    topic_lookup[topic](message)

print("Patient with id 99:", DB.getPatientName(99))

mqtt = MQTT(ip="51.83.42.157", port=1883, qos=2, mode=Message_mode.BLOCKING)
#mqtt = MQTT(ip="iot.eclipse.org", port=1883, qos=2, mode=Message_mode.BLOCKING)
mqtt.message_callback = message_callback
mqtt.sub_to_topics(["database/message", "database/measurement"])
try:
    mqtt.connect()
except KeyboardInterrupt:
    mqtt.disconnect()
    print("Bye!")