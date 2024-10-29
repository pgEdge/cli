
import os
import util

pge=f"{os.getenv('MY_HOME')}/{os.getenv('MY_CMD')}"

isAutoStart = str(os.getenv("isAutoStart", "False"))
isSTART = str(os.getenv("isSTART", "False"))
util.message(f"install-kirk.py isAutoStart = {isAutoStart}, isSTART = {isSTART}", "debug")

pidfile = f"{util.getreqenv('MY_DATA')}/kirk.pid"
util.set_column("pidfile", "kirk", pidfile)

if isAutoStart == "True":
    util.set_column("autostart", "kirk", 1)
    isSTART = "True"

conf=f"{os.getenv('HOME')}/.kirk.conf"
util.message(f"looking for config file: {conf}")
if os.path.isfile(conf):
    util.message(f"running file: {conf}")
    os.system(conf)


if isSTART == "True":
   os.system(f"{os.getenv('MY_HOME')}/{os.getenv('MY_CMD')} start kirk")
