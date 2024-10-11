#!/usr/bin/env python3

import os, sys, time, subprocess, json
import paho.mqtt.client as paho
from paho import mqtt

import util

HOST = util.getreqval("KIRK", "HOST")
PORT = util.getreqval("KIRK", "PORT", isInt=True)
USER = util.getreqval("KIRK", "USER")
PASSWD = util.getreqval("KIRK", "PASSWD")
CUSTOMER = util.getreqval("KIRK","CUSTOMER" )
CLUSTER = util.getreqval("KIRK", "CLUSTER")
NODE = util.getreqval("KIRK", "NODE")

TOPIC = f"cli/{CUSTOMER}/{CLUSTER}/{NODE}"

MY_HOME = util.getreqenv("MY_HOME")
MY_DATA = util.getreqenv("MY_DATA")
MY_LOGS = util.getreqenv("MY_LOGS")


def run_cli_command(p_cmd):
    """Run a command while capturing the live output"""

    cmd = f"{os.getenv('PSX')}/pgedge {p_cmd} --json"
    cmd_l = cmd.split()
    err_kount = 0

    try:
      process = subprocess.Popen(
        cmd_l,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
      )
      while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break

        clean_line = line.decode().strip()

        rc = process_output_line(clean_line, str(cmd_l[1]))
        err_kount = err_kount + rc

    except Exception as e:
        print(f"ERROR: Processing output: {e}")
        return(1)

    publish_message('[{"rc": "' + str(err_kount) + '"}]')

    if err_kount > 0:
        return(1)

    return(0)


def process_output_line(p_line, p_cmd):
    
  if p_line == "":
      return(0)

  rc = 0
  try:
      jj = json.loads(p_line)
      if p_line.startswith('[{"type": "error",'):
          rc = 1
      elif p_line.startswith('[{"type"'):
          pass
      elif p_cmd in ["info", "list"]:
          ## these data commands pass "funky" json
          pass
      else:
          ## this is a funky line thats ignored (for now)
          pass

  except Exception as e:
      util.message(f"turn it into json: {e}", "debug")
      ## turn it into json info
      out_j = {}
      out_j["type"] = "info"
      out_j["msg"] = p_line
      print(f"[{json.dumps(out_j)}]")
      return(0)

  publish_message(p_line)
  return(rc)


def publish_message(p_msg):
    print(p_msg)
    client.publish(topic=f"{TOPIC}/out", payload=p_msg, qos=0)


def on_connect(client, userdata, flags, rc, properties=None):
    util.message(f"kirk on_connect() CONNACK received with code {rc}.", "debug")


def on_publish(client, userdata, mid, properties=None):
    util.message(f"kirk on_publish() {mid}.", "debug")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    util.message(f"kirk on_subscribe() {mid}  {granted_qos}", "debug")


def on_message(client, userdata, msg):
    payload = msg.payload
    cmd = payload.decode("utf-8")

    util.message(f"kirk on_message({cmd})", "debug")

    run_cli_command(cmd)


## MAINLINE ########################################################

pidfile = f"{MY_DATA}/kirk.pid"
this_pid = os.getpid()
if os.path.exists(pidfile):
    util.exit_message(f"Process already running. (check '{pidfile}')", 0)
else:
    os.system(f"echo '{this_pid}' > {pidfile}")

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(USER, PASSWD)
client.connect(HOST, PORT)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe(TOPIC, qos=0)

client.loop_forever()
