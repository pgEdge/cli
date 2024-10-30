
import os
import util

pge=f"{os.getenv('MY_HOME')}/{os.getenv('MY_CMD')}"

conf=f"{os.getenv('HOME')}/.kirk.conf"
util.message(f"looking for config file: {conf}")
if os.path.isfile(conf):
    util.message(f"running file: {conf}")
    os.system(conf)
