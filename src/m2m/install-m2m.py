
import os
import util

isAutoStart = str(os.getenv("isAutoStart", "False"))
isSTART = str(os.getenv("isSTART", "False"))
util.message(f"install-m2m.py isAutoStart = {isAutoStart}, isSTART = {isSTART}", "debug")

m2m_pidfile = f"{util.getreqenv('MY_DATA')}/m2m.pid"
util.set_column("pidfile", "m2m", m2m_pidfile)

if isAutoStart == "True":
    util.set_column("autostart", "m2m", 1)
    isSTART = "True"

if isSTART == "True":
   os.system(f"{os.getenv('MY_HOME')}/{os.getenv('MY_CMD')} start m2m")
