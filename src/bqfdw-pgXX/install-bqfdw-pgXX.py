 
####################################################################
######          Copyright (c)  2020-2022 PGSQL.IO         ##########
####################################################################

import util, os, sys

bqfdwV = str(sys.argv[1])
cmd="python3 -m pip install --user bigquery-fdw=='" + bqfdwV + "'"
print('   ' + cmd)
os.system(cmd)

