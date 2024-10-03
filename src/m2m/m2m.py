#!/usr/bin/env python3

import os, sys, time, subprocess
import paho.mqtt.client as paho
from paho import mqtt

import util

BROKER_HOST = util.getreqval("PGEDGE", "BROKER_HOST")
BROKER_PORT = util.getreqval("PGEDGE", "BROKER_PORT", isInt=True)
BROKER_USER = util.getreqval("PGEDGE", "BROKER_USER")
BROKER_PASSWD = util.getreqval("PGEDGE", "BROKER_PASSWD")

CLIENT = util.getreqval("PGEDGE","CLIENT_ID" )
CLUSTER = util.getreqval("PGEDGE", "CLUSTER_ID")
NODE = util.getreqval("PGEDGE", "NODE_ID")
TOPIC = f"cli/{CLIENT}/{CLUSTER}/{NODE}"

MY_HOME = util.getreqenv("MY_HOME")
MY_DATA = util.getreqenv("MY_DATA")
MY_LOGS = util.getreqenv("MY_LOGS")


def run_cli_command(cmd):
    ## os.system(f"{MY_HOME}/pgedge {cmd} --json")
    full_cmd = f"{MY_HOME}/pgedge {cmd} --json"
    process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, ""):
        sys.stdout.write(line)


def on_connect(client, userdata, flags, rc, properties=None):
    util.message(f"m2m on_connect() CONNACK received with code {rc}.", "debug")


def on_publish(client, userdata, mid, properties=None):
    util.message(f"m2m on_publish() {mid}.", "debug")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    util.message(f"m2m on_subscribe() {mid}  {granted_qos}", "debug")


def on_message(client, userdata, msg):
    payload = msg.payload
    cmd = payload.decode("utf-8")

    util.message(f"m2m on_message({cmd})", "debug")

    run_cli_command(cmd)


## MAINLINE ########################################################

m2m_pidfile = f"{MY_DATA}/m2m.pid"
this_pid = os.getpid()
if os.path.exists(m2m_pidfile):
    util.exit_message(f"Process already running. (check '{m2m_pidfile}')", 0)
else:
    os.system(f"echo '{this_pid}' > {m2m_pidfile}")

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(BROKER_USER, BROKER_PASSWD)
client.connect(BROKER_HOST, BROKER_PORT)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe(TOPIC, qos=0)

client.loop_forever()
