import os, sys, psutil

import util


def whack_pidfile():
    os.system(f"rm -f {util.getreqenv('MY_DATA')}/m2m.pid")


process_name = "m2m.py"
processes = psutil.process_iter()
for process in processes:
    try:
        if process_name == process.name() or process_name in process.cmdline():
            util.message(f"killing pid {process.pid}")
            process.terminate()
            whack_pidfile()
            sys.exit(0)
    except Exception as e:
        util.message(f"{e}")
        sys.exit(1)

whack_pidfile()
util.message(f"{process_name} not running")
sys.exit(0)
