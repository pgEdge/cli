import os, sys, time
import util, startup

startup.start_linux("postgrest")
time.sleep(3)
startup.status_linux("postgrest --lines 25 --full --no-pager")