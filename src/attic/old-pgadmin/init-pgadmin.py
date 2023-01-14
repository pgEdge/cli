from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2015-2020 BigSQL           ##########
####################################################################

import argparse, util, os, sys, shutil, subprocess, getpass, json
import startup

MY_HOME = os.getenv('MY_HOME', '')

sys.path.append(os.path.join(MY_HOME, 'hub', 'scripts', 'lib'))

from ConsoleLogger import ConsoleLogger

def fatal_error(p_msg):
  if isJson:
    sys.stdout = previous_stdout
    jsonMsg = {}
    jsonMsg['status'] = "error"
    jsonMsg['msg'] = p_msg
    print(json.dumps([jsonMsg]))
  else:
    print(p_msg)
  sys.exit(1)
  return

#######################################################
##                     MAINLINE                      ##
#######################################################

isJson = os.getenv("isJson", None)

app_datadir = util.get_comp_datadir("pgadmin")
update_install_date=False
if app_datadir == "":
  update_install_date=True

parser = argparse.ArgumentParser()
parser.add_argument("--datadir", type=str, default="")
parser.add_argument("--port", type=int, default=80)
parser.add_argument("--pwfile", type=str, default="")
parser.add_argument("--email", type=str, default="")
args = parser.parse_args()

isSilent = os.getenv("isSilent", None)

## Initialize the ConsoleLogger to redirect the console output log file
previous_stdout = sys.stdout
sys.stdout = ConsoleLogger()

print(" ")
print("## Initializing pgadmin #######################")

if args.email > "":
  i_email = args.email
else:
  i_email = util.get_email_address()


## PORT ###############################################
if args.port > 0:
  i_port = args.port
else:
  i_port =  util.get_avail_port("pgAdmin Port", 80, pgver)


## DATA ###############################################
data_root = os.path.join(MY_HOME, "data")
if not os.path.isdir(data_root):
  os.mkdir(data_root)

if args.datadir == "":
  pgadmin_data = os.path.join(data_root, "pgadmin")
else:
  pgadmin_data = args.datadir

if not os.path.isdir(pgadmin_data):
  os.mkdir(pgadmin_data)


## PASSWD #############################################
is_password=False
pass_file=""
if args.pwfile:
  pass_file = args.pwfile
  if not os.path.isfile(pass_file):
    fatal_error("Error: Invalid --pwfile")

if os.path.isfile(pass_file):
  file = open(pass_file, 'r')
  line = file.readline()
  password = line.rstrip()
  file.close()
else:
  password = util.get_superuser_passwd("pgAdmin")


## INITIALIZE #########################################
print('\nInitializing pgAdmin with:')

cmd="sudo docker pull dpage/pgadmin4"
print("  " + cmd)
err = os.system(cmd)
if err:
  print("rc(" + str(err) + ")")
  fatal_error("Docker run error")

run_options = ""

cmd='sudo docker run --name pgadmin -p ' + str(i_port) + ':80' + \
    ' -e PGADMIN_DEFAULT_EMAIL="' + i_email + '"' + \
    ' -e PGADMIN_DEFAULT_PASSWORD="' + password + '"' + run_options + \
    ' -d dpage/pgadmin4'
print("  " + cmd)
err = os.system(cmd)
if err:
  print("rc("+ str(err) + ")")
  fatal_error("Docker run error")


if isJson:
  sys.stdout = previous_stdout
  msg = '[{"status":"complete","msg":"Initialization completed.","component":"pgadmin"}]'
  print(msg)

