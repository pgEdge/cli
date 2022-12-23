import os

import util

isAutoStart = str(os.getenv("isAutoStart", "False"))
isSTART = str(os.getenv("isSTART", "False"))

if isSTART == "True":
  util.message("Starting pgBouncer")
  MY_CMD = os.getenv('MY_CMD')
  MY_HOME = os.getenv('MY_HOME')
  start_cmd = MY_HOME + os.sep + MY_CMD + " start bouncer"
  os.system(start_cmd)

if isAutoStart == "True":
  util.message("WIP Bouncer Autostart")



