#!/usr/bin/env python3

"""
A full life-cycle Python MQTT NodeCtl Prototype
"""
import logging
import signal
import sys
import json
from time import sleep
import paho.mqtt.client as mqtt

# Initialize Logging
logging.basicConfig(level=logging.WARNING)  # Global logging configuration
logger = logging.getLogger("main")  # Logger for this module
logger.setLevel(logging.INFO) # Debugging for this file.

# Global Variables
BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "NodeCtlClient"
TOPIC = "nodectl"
client = None  # MQTT client instance. See init_mqtt()
led = None     # PWMLED Instance. See init_led()


"""
MQTT Related Functions and Callbacks
"""
def on_connect(client, user_data, flags, connection_result_code):
    """on_connect is called when our program connects to the MQTT Broker.
       Always subscribe to topics in an on_connect() callback.
       This way if a connection is lost, the automatic
       re-connection will also results in the re-subscription occurring."""

    if connection_result_code == 0:
        # 0 = successful connection
        logger.info("Connected to MQTT Broker")
    else:
        # connack_string() gives us a user friendly string for a connection code.
        logger.error("Failed to connect to MQTT Broker: " + mqtt.connack_string(connection_result_code))

    # Subscribe to the topic for LED level changes.
    client.subscribe(TOPIC, qos=2)



def on_disconnect(client, user_data, disconnection_result_code):
    """Called disconnects from MQTT Broker."""
    logger.error("Disconnected from MQTT Broker")



def on_message(client, userdata, msg):
    """Callback called when a message is received on a subscribed topic."""
    logger.debug("Received message for topic {}: {}".format( msg.topic, msg.payload))

    data = None

    ##try:
    ##    data = json.loads(msg.payload.decode("UTF-8"))
    ##except json.JSONDecodeError as e:
    ##    logger.error("JSON Decode Error: " + msg.payload.decode("UTF-8"))

    if msg.topic == TOPIC:
        print(str(msg.payload)) 
    else:
        logger.error("Unhandled message topic {} with payload " + str(msg.topic, msg.payload))



def signal_handler(sig, frame):
    """Capture Control+C and disconnect from Broker."""
    global led_state

    logger.info("You pressed Control + C. Shutting down, please wait...")

    client.disconnect() # Graceful disconnection.
    ##led.off()
    sys.exit(0)



def init_mqtt():
    global client

    # Our MQTT Client. See PAHO documentation for all configurable options.
    # "clean_session=True" means we don"t want Broker to retain QoS 1 and 2 messages
    # for us when we"re offline. You"ll see the "{"session present": 0}" logged when
    # connected.
    client = mqtt.Client(
        client_id=CLIENT_ID,
        clean_session=False)

    # Route Paho logging to Python logging.
    client.enable_logger()

    # Setup callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to Broker.
    client.connect(BROKER_HOST, BROKER_PORT) 


# Initialise Module
init_mqtt()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Capture Control + C
    logger.info("Listening for messages on topic '" + TOPIC + "'. Press Control + C to exit.")

    client.loop_start()
    signal.pause()
