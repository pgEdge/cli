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
    cmd_l = cmd.split()

    result = subprocess.run(cmd, text=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    rso = result.stdout
    ret_j = []
    for ln in rso.splitlines():
        try:
            jj = json.loads(ln)
            ret_j.append(jj)
        except Exception as e:
            print(f"DEBUG: exceptional line: '{ln}' len = {len(ln)}")
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

    ### the below is test code and never (presently) executed
    ###  it is an attempt to iterate thru a stream of stdout messages
    ###  as they occur in order to give interactive feedback.  The
    ###  problem seems that of thread blocking/interference between
    ###  PAHO and looping thru the subprocess.Popen)
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
        print(f"DEBUG: stdout.clean_line {clean_line}")

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
    """Process each output line."""
    
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
            ## these data commands pass custom json 
            pass
        else:
            ## this is a funky line thats ignored (for now)
            util.mesage(f"ignoring this json line for now: '{p_line}'", "debug")
            pass

    except Exception as e:
        util.message(f"turn it into json: {e}", "debug")
        ## turn it into json info
        out_a = []
        out_j = {}
        out_j["type"] = "info"
        out_j["msg"] = p_line
        out_a.append(out_j)
        print(json.dumps(out_a))
        return(0)

    print("DEBUG2 process output line")
    publish_message(p_line)
    return(rc)


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
    #if rc != 0:
    #    util.message(f"Unexpected disconnection with rc = {rc}")
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

pidfile = f"{MY_DATA}/kirk.pid"
this_pid = os.getpid()
if os.path.exists(pidfile):
    util.exit_message(f"Process already running. (check '{pidfile}')", 0)
else:
    os.system(f"echo '{this_pid}' > {pidfile}")

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

