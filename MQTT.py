import paho.mqtt.client as mqtt
from Message import Message
from Measurement import Measurement
from typing import List, Tuple
from enum import Enum
import socket


# enum for modes
# in blocking mode, the class will block the thread and just receive messages
# in non blocking mode, the class will not block the thread and code will keep running
class Message_mode(Enum):
    BLOCKING = 0
    NON_BLOCKING = 1


# MQTT Class Version 0.17
# wrapper around the paho mqtt library to make life a bit easier.
class MQTT:
    # error messages:
    __ERROR_INVALID_QOS = "Quality of service can only be 0, 1, or 2. %d given"
    __ERROR_INVALID_IP = "Invalid IP given"
    __ERROR_INVALID_TOPIC_NAME = "Invalid topic name"
    __ERROR_COULD_NOT_CONNECT = "Could not connect to broker with ip=%s and port=%d"
    __ERROR_DISCONNECT_WHILE_NOT_CONNECTED = "Can't disconnect from client, not yet connected"
    __ERROR_PUBLISH_WHILE_NOT_CONNECTED = "Can't publish a message when not connected yet"

    # log messages:
    __LOG_BROKER_CONNECT = "Connected to broker with IP %s"
    __LOG_BROKER_DISCONNECT = "Disconnected from client"
    __LOG_MESSAGE_RECEIVED = "message \"%s\" received on topic %s"
    __LOG_BAD_CONNECTION = "Bad connection, returned code %d"

    # constructor function
    # ip (string): ip of broker to connect to
    # port (int): port of broker to connect to
    # qos (int, 0<=qos<=2): qos value in the MQTT protocol
    # mode (int, BLOCKING/NON_BLOCKING): defines the mode to run in
    #
    # the constructor function only changes the state of the object, connecting happens with the connect function
    def __init__(self, ip: str, port: int, qos: int, mode: Message_mode = Message_mode.NON_BLOCKING):
        if qos > 2 or qos < 0:
            raise ValueError(self.__ERROR_INVALID_QOS % qos)
        if ip is None or ip == "":
            raise ValueError(self.__ERROR_INVALID_IP)

        self.message_callback = None

        self._ip = ip
        self._port = port
        self._qos = qos
        self._topics = []
        self._mode = mode

        self._client = mqtt.Client('', True, None, mqtt.MQTTv31)
        self._client.on_connect = self.__on_connect
        self._client.on_log = self.__on_log
        self._client.on_disconnect = self.__on_disconnect
        self._client.on_message = self.__on_message

        self._connected = False

    # function to connect to the broker described when creating the object
    def connect(self) -> None:
        try:
            self._client.connect(self._ip, self._port)
            self._connected = True
            if self._mode == Message_mode.NON_BLOCKING:
                self._client.loop_start()
            elif self._mode == Message_mode.BLOCKING:
                self._client.loop_forever()
        except socket.gaierror as err:
            raise ValueError(self.__ERROR_COULD_NOT_CONNECT % (self._ip, self._port))
        print("connected variable:", self._connected)

    # disconnect from the broker, if currently connected to one
    def disconnect(self) -> None:
        
        if self._connected:
            self._client.disconnect()
            if self._mode == Message_mode.NON_BLOCKING: self._client.loop_stop()
        else:
            raise Exception(self.__ERROR_DISCONNECT_WHILE_NOT_CONNECTED)

    # function to subscribe to multiple topics. These topics will not be actually subscribed to until a connection is made with the broker
    # list (list of strings): topics to subscribe to
    # message_callback (function): a function to run when a message is received. This function receives one argument which is the message received as a string
    def sub_to_topics(self, list: List[str]) -> None:
        for topic in list:
            if topic is None or len(topic) == 0:
                raise ValueError(self.__ERROR_INVALID_TOPIC_NAME)
            self._topics.append((topic, self._qos))

    # function to subscribe a topic. This topic will not be actually subscribed to until a connection is made with the broker
    # topic (string): topic to subscribe to
    # message_callback (function): a function to run when a message is received. This function receives two arguments
    #                              which is the topic and the message both received as a string
    def sub_to_topic(self, topic: str) -> None:
        if topic is None or len(topic) == 0:
            raise ValueError(self.__ERROR_INVALID_TOPIC_NAME)
        self._topics.append((topic, self._qos))

    # function to publish a message, once a connection has been made
    # topic (string): topic to publish to
    # message (Message): message to send
    def publish_message(self, topic: str, message: Message) -> None:
        if topic is None or len(topic) == 0:
            raise ValueError(self.__ERROR_INVALID_TOPIC_NAME)

        if (self._connected):
            self._client.publish(topic, str(message))
        else:
            raise Exception(self.__ERROR_PUBLISH_WHILE_NOT_CONNECTED)
    

    # function to publish a measurement, once a connection has been made
    # topic (string): topic to publish to
    # measurement (Measurement): measurement to send
    def publish_measurement(self, topic: str, measurement: Measurement) -> None:
        if topic is None or len(topic) == 0:
            raise ValueError(self.__ERROR_INVALID_TOPIC_NAME)

        if (self._connected):
            self._client.publish(topic, str(measurement))
        else:
            raise Exception(self.__ERROR_PUBLISH_WHILE_NOT_CONNECTED)

    # function to log something
    # text (string): what to log
    def _log(self, text: str) -> None:
        print("MQTT log:", text)

    # function which runs on connection with a broker
    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._log(self.__LOG_BROKER_CONNECT % self._ip)
            self._client.subscribe(self._topics)
        else:
            self._log(self.__LOG_BAD_CONNECTION % rc)

    # function which runs on disconnection with a broker
    def __on_disconnect(self, client, userdata, flags, rc=0):
        self._connected = False
        self._log(self.__LOG_BROKER_DISCONNECT)

    # function which runs when the mqtt library logs something (connection, errors, pings, etc.)
    def __on_log(self, client, userdata, level, buf):
        self._log(buf)

    # function which runs on receiving a message, will call the callback function which is supplied by the user when subscribing to a topic
    def __on_message(self, client, userdata, message_raw):
        topic = message_raw.topic
        m_decode = str(message_raw.payload.decode("utf-8", "strict"))
        self._log(self.__LOG_MESSAGE_RECEIVED % (m_decode, topic))
        if self.message_callback != None:
            obj = None
            if Message.is_str_message(m_decode):
                obj = Message.from_string(m_decode)
            elif Measurement.is_str_measurement(m_decode):
                obj = Measurement.from_string(m_decode)
            else:
                obj = m_decode
            self.message_callback(topic, obj)