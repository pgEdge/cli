import os, sys, psutil

import util


def whack_pidfile():
    os.system(f"rm -f {util.getreqenv('MY_DATA')}/kirk.pid")


processes = psutil.process_iter()
for process in processes:
    try:
        if process.name() == "python3":
            cmdline = str(process.cmdline()[1])
            if cmdline.endswith("kirk.py"):
                util.message(f"killing kirk pid {process.pid}")
                process.terminate()
                whack_pidfile()
                sys.exit(0)
    except Exception as e:
        util.message(f"{e}")
        sys.exit(1)

whack_pidfile()
util.message("kirk not running")
sys.exit(0)
