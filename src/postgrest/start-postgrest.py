
import os, sys, time
import util

os.system("sudo systemctl start postgrest")

time.sleep(3)
os.system("sudo systemctl status postgrest --lines 25 --full --no-pager")
