
import os
import util

isAutoStart = str(os.getenv("isAutoStart", "False"))
isSTART = str(os.getenv("isSTART", "False"))
util.message(f"install-kirk.py isAutoStart = {isAutoStart}, isSTART = {isSTART}", "debug")

pidfile = f"{util.getreqenv('MY_DATA')}/kirk.pid"
util.set_column("pidfile", "kirk", pidfile)

if isAutoStart == "True":
    util.set_column("autostart", "kirk", 1)
    isSTART = "True"

if isSTART == "True":
   os.system(f"{os.getenv('MY_HOME')}/{os.getenv('MY_CMD')} start kirk")
