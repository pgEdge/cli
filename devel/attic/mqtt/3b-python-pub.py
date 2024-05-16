#!/usr/bin/env python3

import sys, os
import paho.mqtt.client as mqtt
from dotenv.main import load_dotenv

msg = "INFO"
if len(sys.argv) == 2:
  msg = sys.argv[1]

load_dotenv("./env.sh")
 
BROKER_HOST = os.getenv("BROKER_HOST")
BROKER_PORT = int(os.getenv("BROKER_PORT")) 
CLIENT_ID = os.getenv("CLIENT_ID")
TOPIC = os.getenv("TOPIC")

mqtt_client = mqtt.Client(CLIENT_ID)

print(f"# mqtt_client.connect(host={BROKER_HOST}, port={BROKER_PORT})")
mqtt_client.connect(host=BROKER_HOST, port=BROKER_PORT)

print(f"# mqtt_client.publish({TOPIC}, '{msg}')")
mqtt_client.publish(TOPIC, msg)
