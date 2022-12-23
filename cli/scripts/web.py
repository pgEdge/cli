import flask, os, subprocess
from flask import request, jsonify
from subprocess import Popen, PIPE, STDOUT

import sys

import util, api

io_cmd = os.getenv('MY_HOME') + os.sep + os.getenv('MY_CMD')

app = flask.Flask(__name__)


def sys_cli(p_cmd): 
  cmd = io_cmd + " " + p_cmd + " --json"
  p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, executable=None, close_fds=False)
  (out, err) = p.communicate()
  return(out.decode('utf8'))


@app.route('/', methods=['GET'])
def home():
    return '''<h1>NDCTL API</h1>
<p>A development API over "ndctl" commands</p>'''


@app.route('/info', methods=['GET'])
def info():
  i = sys_cli("info")
  return (i)


@app.route('/cloud/create', methods=['GET'])
def cloud_create():
  prv = request.args.get('provider')
  if prv in (None, ""):
    util.message("'provider' parm required.", "ERROR", True)
    return("[]")
    
  i = sys_cli("cloud create " + prv)
  return (i)


@app.route('/node/create', methods=['GET'])
def node_create():
  return


@app.route('/node/destroy', methods=['GET'])
def node_destroy():
  return


@app.route('/node/reboot', methods=['GET'])
def node_reboot():
  return


@app.route('/node/start', methods=['GET'])
def node_start():
  return


@app.route('/node/stop', methods=['GET'])
def node_stop():
  return


def test_required(req_args, p_arg):
  arg = req_args.get(p_arg)
  if arg in (None, ""):
    util.message("required arg '" + str(p_arg) + "' missing", "error", True)
    return False
  return True


@app.route('/node/list', methods=['GET'])
def node_list():
  if test_required(request.args, "cloud") == False:
    return("")

  cld = request.args.get("cloud")
  i = sys_cli("node list " + cld)
  return (i)


if __name__ == "__main__":
  app.run()
