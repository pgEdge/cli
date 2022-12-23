from __future__ import print_function, division
 
####################################################################
######          Copyright (c)  2015-2019 BigSQL           ##########
####################################################################

import sys
import sqlite3
import datetime

sqlite_file = sys.argv[1]

section   = sys.argv[2]
s_key     = sys.argv[3]
s_value   = sys.argv[4]

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

sql = "DELETE FROM settings WHERE section = ? AND s_key = ?"
c.execute(sql, [section, s_key])
sql = "INSERT INTO settings  VALUES (?, ?, ?)"
c.execute(sql, [section, s_key, s_value])

conn.commit()
conn.close()


