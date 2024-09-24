#!/usr/bin/env python3

import os, sys, time
import paho.mqtt.client as paho
from paho import mqtt

try:
    from dotenv.main import load_dotenv
    load_dotenv("./env.sh")

    BROKER_HOST = os.getenv("BROKER_HOST")
    BROKER_PORT = int(os.getenv("BROKER_PORT"))
    BROKER_USER = os.getenv("BROKER_USER")
    BROKER_PASSWD = os.getenv("BROKER_PASSWD")
    TOPIC = os.getenv("TOPIC")
    PGEDGE_HOME = os.getenv("PGEDGE_HOME")
except Exception as e:
    print(f"ERROR loading ENV: {e}")
    sys.exit(1)

def run_cli_command(cmd):
    os.system(f"{PGEDGE_HOME}/pgedge {cmd} --json")

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    payload = msg.payload
    run_cli_command(payload.decode("utf-8"))


client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(BROKER_USER, BROKER_PASSWD)
client.connect(BROKER_HOST, BROKER_PORT)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe(f"{TOPIC}/#", qos=0)

client.loop_forever()
