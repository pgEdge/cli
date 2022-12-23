from __future__ import print_function, division

####################################################################
######          Copyright (c)  2015-2019 BigSQL           ##########
####################################################################

import sys
import sqlite3
import datetime

sqlite_file = sys.argv[1]

component = sys.argv[2]
project   = sys.argv[3]
version   = sys.argv[4]
platform  = sys.argv[5]
port      = sys.argv[6]
status    = sys.argv[7]

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

c.execute("INSERT INTO components VALUES ('" + \
           component + "','" + project + "','" + version + "','" +  platform + "'," + \
           port + ",'" + status + "','" + str(datetime.datetime.now()) + "','off', '', '', '', '', '')")

conn.commit()
conn.close()


