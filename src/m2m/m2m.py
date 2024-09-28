#!/usr/bin/env python3

import os, sys, time
import paho.mqtt.client as paho
from paho import mqtt

import util

BROKER_HOST = util.getreqenv("M2M_BROKER_HOST")
BROKER_PORT = util.getreqenv("M2M_BROKER_PORT", isInt=True)
BROKER_USER = util.getreqenv("M2M_BROKER_USER")
BROKER_PASSWD = util.getreqenv("M2M_BROKER_PASSWD")
TOPIC = util.getreqenv("M2M_TOPIC")


def run_cli_command(cmd):
    os.system(f"{os.getenv('MY_HOME')}/pgedge {cmd} --json")

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
