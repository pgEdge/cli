#!/usr/bin/env python3

import os, sys, time, subprocess, json
import paho.mqtt.client as paho
from paho import mqtt

import util

HOST = util.getreqval("KIRK", "HOST", verbose=True)
PORT = util.getreqval("KIRK", "PORT", isInt=True)
USER = util.getreqval("KIRK", "USER", verbose=True)
PASSWD = util.getreqval("KIRK", "PASSWD")
CUSTOMER = util.getreqval("KIRK","CUSTOMER", verbose=True )
CLUSTER = util.getreqval("KIRK", "CLUSTER", verbose=True)
NODE = util.getreqval("KIRK", "NODE", verbose=True)

TOPIC = f"cli/{CUSTOMER}/{CLUSTER}/{NODE}"

MY_DATA = util.getreqenv("MY_DATA")
MY_LOGS = util.getreqenv("MY_LOGS")
MY_HOME = util.getreqenv("MY_HOME")
MY_CMD = util.getreqenv("MY_CMD") 


def run_command(p_cmd):
    """Run a command while capturing the output stream of messages"""

    cmd = f"{MY_HOME}/{MY_CMD} {p_cmd} --json"

    result = subprocess.run(cmd, text=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    rso = result.stdout
    ret_j = []
    for ln in rso.splitlines():
        try:
            jj = json.loads(ln)
            ret_j.append(jj)
        except Exception as e:
            if len(ln) > 0:
                ret_j.append(ln)

    rc_j = {}
    rc_j["rc"] = str(result.returncode)
    ret_j.append(rc_j)
    publish_message(json.dumps(ret_j))
    return(0)

    out_p = str(subprocess.check_output(cmd, shell=True), "utf-8")
    for ln in out_p.splitlines():
        publish_message(ln)

    return(0)


def publish_message(p_msg):
    print(p_msg)
    client.publish(topic=f"{TOPIC}/out", payload=p_msg, qos=1)


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        util.message("Connection succesful.")
        client.subscribe(TOPIC, qos=1)
    else:
        util.message(f"Connection failed: {rc}")


def on_disconnect(client, userdata, rc, properties=None):
    pass


def on_publish(client, userdata, mid, properties=None):
    util.message(f"kirk on_publish() {mid}.", "debug")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    util.message(f"kirk on_subscribe() {mid}  {granted_qos}", "debug")


def on_message(client, userdata, msg):
    payload = msg.payload
    cmd = payload.decode("utf-8")

    util.message(f"kirk on_message({cmd})", "debug")

    run_command(cmd)


## MAINLINE ########################################################

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(USER, PASSWD)

while True:
    try:
        client.connect(HOST, PORT)
        time.sleep(1)
        break
    except Exception as e:
        util.message(f"unable to connect: {(e)}", "warn")
        time.sleep(5)

client.loop_forever()

