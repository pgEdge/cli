import os, component

HOME_DIR = os.path.dirname(os.path.realpath(__file__))

component.start_comp('bouncer', HOME_DIR, 'bin/pgbouncer -d pgbouncer.ini')

