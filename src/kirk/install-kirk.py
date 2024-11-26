
import os
import util

pge=f"{os.getenv('MY_HOME')}/{os.getenv('MY_CMD')}"

conf=f"{os.getenv('HOME')}/.kirk.conf"
if os.path.isfile(conf):
    util.message(f"running config file: {conf}")
    os.system(conf)
else:
    util.message(f"could not find config file: {conf}", "warning")
