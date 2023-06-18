#!/usr/bin/env python3

import sys
import paho.mqtt.client as mqtt

msg = "INFO"
if len(sys.argv) == 2:
  msg = sys.argv[1]
 
BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "DenisLussier"
TOPIC = "nodectl"

client = mqtt.Client(CLIENT_ID)

client.connect(host=BROKER_HOST, port=BROKER_PORT)

client.publish(TOPIC, msg)
